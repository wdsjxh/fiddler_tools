<template>
  <div class="app-container">
    <div class="filter-container" style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <span>类型:</span>
        <el-select v-model="search.type" placeholder="请选择">
          <el-option value="web">web</el-option>
          <el-option value="app">app</el-option>
          <el-option value="pc">pc</el-option>
          <el-option value="other">其他</el-option>
        </el-select>
      </div>
      <!-- v-model实现双向绑定,handleFilter事件响应 原生回车事件  -->
      <el-input v-model="search.content" placeholder="内容" style="width: 400px;" @keyup.enter.native="handleFilter" />
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        查询
      </el-button>

      <el-button class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">
        导出
      </el-button>
    </div>
    <el-table
      id="config_tableid"
      v-loading="listLoading"
      :data="list"
      class="config_table"
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
      <el-table-column align="center" label="内容" prop="content" sortable>
        <template slot-scope="scope">
          <pre> {{ scope.row.content }} </pre>
        </template>
      </el-table-column>
      <el-table-column label="类型" prop="type" sortable>
        <template slot-scope="scope">
          <pre> {{ scope.row.type }} </pre>
        </template>
      </el-table-column>

      <el-table-column align="center" prop="time" label="建立时间" width="200" sortable>
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.time }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作">
        <template slot-scope="scope">

          <el-button
            v-if="edit_save_flag_list[scope.$index]"
            size="mini"
            @click="check_scan_status(scope.$index, scope.row)"
          >运行中</el-button>
          <el-button
            v-else
            icon="start"
            size="mini"
            @click="handleStart(scope.$index, scope.row)"
          >启动</el-button>

          <el-button
            size="mini"
            type="danger"
            @click="handleDelete(scope.$index, scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>

      <el-table-column label="详细配置">
        <template slot-scope="scope">
          <el-dropdown
            size="small"
            split-button
            type="primary"
            trigger="hover"
            @command="handleDropdown"
            @click="handleClick"
          >
            {{ tip_data }}
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item
                v-for="(item,index) in all_config_name"
                :key="index"
                :command="{'id':scope.row.id,'config':item}"
                v-text="item"
              />
            </el-dropdown-menu>
          </el-dropdown>
        </template>
      </el-table-column>

      <el-table-column align="center" label="当前配置" width="200" prop="config_name">
        <template slot-scope="scope">
          <i class="el-icon-setting" />
          <span>{{ scope.row.config_name }}</span>
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
import { project_config } from '@/api/table'
import FileSaver from 'file-saver'
import XLSX from 'xlsx'

export default {
  name: 'Scanconfig',

  filters: {
    statusFilter(status) {
      const statusMap = {
        published: 'success',
        draft: 'gray',
        deleted: 'danger'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      tip_data: '新建扫描配置',
      all_config_name: [], // 所有可选配置
      list: null,
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
      command: {
        'id': null,
        'config': null
      },
      pagesize: [10, 15, 20],
      // 绑定搜索数据
      search: {
        type: null,
        content: null
      },
      edit_save_flag_list: [],
      formLabelWidth: '120px',
      temppage: null,
      templimit: null,
      bind_config: {
        id: null,
        content: null
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
      this.bind_config.content = command.config.toString()
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
      project_config(this.listQuery).then(response => {
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
      project_config(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.exportXLSX()
        this.listQuery.page = this.temppage
        this.listQuery.limit = this.templimit
        this.fetchData()
        this.listLoading = false
      })
    },

    handleStart(index, row) {
      console.log(row.content)
      this.listQuery.start = row.content
      this.listQuery.startid = row.id
      this.fetchData()
      this.edit_save_flag_list[index] = true
      console.log(index)
      console.log(this.edit_save_flag_list[index])
    },

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

    handleDelete(index, row) {
      console.log(index, row)
      console.log(row.id)
      this.listQuery.deleteid = row.id
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
      // 类型也选择
      if (this.search.type !== null && this.search.type !== '' && this.search.type !== 'none') {
        this.listQuery.type = this.search.type
        console.log(this.listQuery.type)
      } else {
        this.listQuery.type = '0'
        console.log(this.listQuery.type)
      }
      // 搜索关键字
      if (this.search.content !== null && this.search.content !== '') {
        this.listQuery.content = this.search.content
        console.log(this.listQuery.content)
      } else {
        this.listQuery.content = '0'
        console.log(this.listQuery.content)
      }
      this.fetchData()
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
