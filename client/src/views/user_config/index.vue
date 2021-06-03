<template>
  <div class="app-container">
    <div class="filter-container" style="display:flex;justify-content:space-between;align-items:center">

      <div>
        <span>状态:</span>
        <el-select v-model="search.type" placeholder="请选择">
          <el-option value="启用">启用</el-option>
          <el-option value="禁用">禁用</el-option>
        </el-select>
      </div>

      <!-- v-model实现双向绑定,handleFilter事件响应 原生回车事件  -->
      <el-input v-model="search.username" placeholder="搜索用户名" style="width: 400px;" @keyup.enter.native="handleFilter" />
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        查询
      </el-button>

      <el-button
        class="filter-item"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >
        添加
      </el-button>

      <el-dialog title="添加配置内容" :visible.sync="add_dialogFormVisible" style="width: 70%;">
        <el-form
          :model="addform"
          label-position
          label-width="90px"
          style="width: 80%; margin-left:50px;"
        >
          <el-form-item label="用户名" prop="username">
            <el-input v-model.trim="addform.username" :readonly="readonly" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="addform.password" :type="passwordType">
              <i slot="suffix" class="el-input__icon el-icon-eye" @click="showPwd">
                <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
              </i>
            </el-input>
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="addform.roles" placeholder="请选择类型">
              <el-option label="超级管理员" value="super-admin" />
              <el-option label="管理员" value="admin" />
              <el-option label="用户" value="user" />
            </el-select>
          </el-form-item>

          <el-form-item label="状态" prop="status">
            <el-switch
              v-model="addform.status"
              inactive-color="#ff4949"
              active-value="1"
              inactive-value="0"
            />
          </el-form-item>

        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="add_dialogFormVisible = false">取 消</el-button>
          <el-button type="primary" @click="handleAdd">确 定</el-button>
          <!--          准备添加事件-->
        </div>
      </el-dialog>

      <el-dialog title="编辑配置内容" :visible.sync="edit_dialogFormVisible" style="width: 70%;">
        <el-form
          :model="editform"
          label-position
          label-width="90px"
          style="width: 80%; margin-left:50px;"
        >

          <el-form-item label="角色">
            <el-select v-model="editform.roles" placeholder="请选择类型">
              <el-option label="超级管理员" value="super-admin" />
              <el-option label="管理员" value="admin" />
              <el-option label="用户" value="user" />
            </el-select>
          </el-form-item>

          <el-form-item label="状态" prop="status">
            <el-switch
              v-model="editform.status"
              inactive-color="#ff4949"
              active-value="1"
              inactive-value="0"
            />
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="edit_dialogFormVisible = false">取 消</el-button>
          <el-button type="primary" @click="handleEditSubmit">确 定</el-button>
        </div>
      </el-dialog>

    </div>
    <el-table
      id="user_config_tableid"
      v-loading="listLoading"
      :data="list"
      class="user_config_table"
      element-loading-text="Loading"
      border
      fit
      highlight-current-row
    >
      <el-table-column align="center" label="ID" width="95" prop="id" sortable>
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="用户名" prop="username" sortable>
        <template slot-scope="scope">
          <pre> {{ scope.row.username }} </pre>
        </template>
      </el-table-column>
      <el-table-column align="center" label="角色" prop="role" sortable>
        <template slot-scope="scope">
          <pre> {{ scope.row.roles }} </pre>
        </template>
      </el-table-column>

      <el-table-column align="center" label="状态" prop="status" sortable>
        <template slot-scope="scope">
          <el-tag
            size="small"
            :type="scope.row.valid | statusFilter"
          >{{ scope.row.valid }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column align="center" prop="time" label="抓包token有效期至" sortable>
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.validtime }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" prop="action" label="操作">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="success"
            @click="handleEdit(scope.$index, scope.row)"
          >编辑</el-button>

          <el-button
            size="mini"
            type="danger"
            @click="handleDelete(scope.$index, scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>

    </el-table>
    <!-- 分页 -->
    <el-pagination
      background
      :current-page.sync="listQuery.page"
      :page-sizes="pagesize"
      :page-size="listQuery.limit"
      layout="total,prev,pager,next,jumper,sizes"
      :total="total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script>
import { user_config } from '@/api/table'
import FileSaver from 'file-saver'
import XLSX from 'xlsx'

export default {
  name: 'Scanconfig',

  filters: {
    statusFilter(status) {
      const statusMap = {
        启用: 'success',
        // draft: 'gray',
        禁用: 'danger'
      }
      return statusMap[status]
    },
    statusChange(status) {
      const statusMapx = {
        1: '启用',
        0: '禁用'
      }
      return statusMapx[status]
    }
  },
  data() {
    return {
      tip_data: '新建扫描配置',
      all_config_name: [], // 所有可选配置
      list: null,
      readonly: false,
      passwordType: 'password',
      pageList: [], // 当前页数据
      currentPage: 1, // 当前页
      total: 0,
      listLoading: true,
      pagelimit: 2, // 页面展示数据条数
      tmpList: [], // 临时搜索结果数据-->
      listQuery: {
        page: 1,
        limit: 15
      },
      add_dialogFormVisible: false, // 添加对话框标识
      edit_dialogFormVisible: false,
      formLabelWidth: '120px',
      addform: {
        roles: null,
        status: null
      },
      editform: {
        username: null,
        roles: null,
        status: null
      },
      command: {
        'id': null,
        'config': null
      },
      pagesize: [10, 15, 20],
      // 绑定搜索数据
      search: {
        type: null,
        username: null
      },
      edit_save_flag_list: [],

      temppage: null,
      templimit: null,
      bind_config: {
        id: null,
        username: null
      }
    }
  },

  created() {
    this.fetchData()
    this.init_edit_save_flag_list()
  },
  methods: {
    handleDropdown(command) {
      this.$message('您已选择配置：' + command.config.toString())
      this.bind_config.id = command.id.toString()
      this.bind_config.username = command.config.toString()
      this.listQuery.bind_config = this.bind_config
      this.fetchData()
    },
    handleClick() {
      this.$message('跳转到扫描规则配置')
      this.$router.replace('/project_config/rule_config')
    },
    init_edit_save_flag_list() {
      this.edit_save_flag_list = new Array(this.listQuery.limit)
    },

    fetchData() {
      // 添加username参数
      this.listQuery.username = this.$store.getters.name
      this.listQuery.token = this.$store.getters.token
      this.listLoading = true
      user_config(this.listQuery).then(response => {
        this.list = response.data.items
        console.log(response)
        this.all_config_name = response.data.all_config_name
        this.total = response.data.total
        this.listLoading = false
      })
    },
    // 单独导出逻辑
    downloadData() {
      this.listLoading = true
      user_config(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.exportXLSX()
        this.listQuery.page = this.temppage
        this.listQuery.limit = this.templimit
        this.fetchData()
        this.listLoading = false
      })
    },

    // handleStart(index, row) {
    //   console.log(row.username)
    //   this.listQuery.start = row.username
    //   this.listQuery.startid = row.id
    //   this.fetchData()
    //   this.edit_save_flag_list[index] = true
    //   console.log(index)
    //   console.log(this.edit_save_flag_list[index])
    // },

    check_scan_status(index, row) {
      console.log('to check_scan_status')
    },

    handleDownload() {
      console.log('handleDownload')
      this.temppage = this.listQuery.page
      this.templimit = this.listQuery.limit

      this.listQuery.page = 1
      this.listQuery.limit = 99999999

      this.downloadData()
      /* 你的逻辑代码 */

      // this.exportExcel()
    },

    exportXLSX() {
      const ws = XLSX.utils.json_to_sheet(this.list)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, 'sheetname')
      return XLSX.writeFile(wb, 'filename.xlsx')
    },

    exportExcel() {
      /* generate workbook object from table */
      var wb = XLSX.utils.table_to_book(document.querySelector('.el-table'))
      /* get binary string as output */
      var wbout = XLSX.write(wb, { bookType: 'xlsx', bookSST: true, type: 'array' })
      try {
        FileSaver.saveAs(new Blob([wbout], { type: 'application/octet-stream' }), 'sheetjs.xlsx')
      } catch (e) { if (typeof console !== 'undefined') console.log(e, wbout) }
      return wbout
    },

    handleCreate() {
      this.add_dialogFormVisible = true
      this.edit_dialogFormVisible = false
    },

    handleAdd() {
      this.listQuery.add = JSON.stringify(this.addform)
      this.addform.roles = null
      this.addform.status = null
      this.add_dialogFormVisible = false
      this.fetchData()
    },

    handleEdit(index, row) {
      this.editform.username = row.username
      this.edit_dialogFormVisible = true
      this.add_dialogFormVisible = false
    },

    handleEditSubmit() {
      this.listQuery.edit = JSON.stringify(this.editform)
      this.editform.roles = null
      this.editform.status = null
      this.edit_dialogFormVisible = false
      this.fetchData()
    },

    handleDelete(index, row) {
      console.log(row)
      this.listQuery.delete_user = row.username
      this.fetchData()
    },

    // 改变页面条数
    handleSizeChange: function(size) {
      console.log(size)
      this.listQuery.limit = size
      this.fetchData()
    },

    // 改变当前页
    handleCurrentChange: function(currentPage) {
      console.log(currentPage)
      this.listQuery.page = currentPage
      this.fetchData()
    },
    // 筛选格式
    handleFilter: function() {
      // this.listQuery.searchflag = 1 // username 冲突问题
      // 类型也选择
      if (this.search.type !== null && this.search.type !== '' && this.search.type !== 'none') {
        this.listQuery.valid = this.search.type
      } else {
        this.listQuery.valid = '0'
      }
      // 搜索关键字
      if (this.search.username !== null && this.search.username !== '') {
        this.listQuery.myuser = this.search.username
      } else {
        this.listQuery.myuser = '0'
      }
      this.fetchData()
    },
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
    }

  }

}
</script>

<style scoped>
  .edit-input {
    padding-right: 100px;
  }
  .cancel-btn {
    position: absolute;
    right: 15px;
    top: 10px;
  }
</style>
