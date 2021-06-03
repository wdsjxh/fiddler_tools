<template>
  <div class="app-container">
    <!--      <div  class="filter-container" style="width: 100%;margin-top:30px;margin-left:30px">-->
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
      <el-button class="filter-item" type="primary" icon="el-icon-edit" @click="dialogFormVisible = true">
        新建项目
      </el-button>

      <el-dialog title="添加配置内容" :visible.sync="dialogFormVisible">
        <el-form :model="addform">
          <el-form-item label="类型" :label-width="formLabelWidth">
            <el-select v-model="addform.type" placeholder="请选择类型">
              <el-option label="web" value="web" />
              <el-option label="app" value="app" />
              <el-option label="pc" value="pc" />
            </el-select>
          </el-form-item>
          <el-form-item label="项目内容" :label-width="formLabelWidth">
            <el-input v-model="addform.content" autocomplete="off" />
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialogFormVisible = false">取 消</el-button>
          <el-button type="primary" @click="handleAdd">确 定</el-button>
        <!--          准备添加事件-->
        </div>
      </el-dialog>

      <el-dialog title="编辑配置内容" :visible.sync="edit_dialogFormVisible">
        <el-form :model="editform">
          <el-form-item label="类型" :label-width="formLabelWidth">
            <el-select v-model="editform.type" placeholder="请选择类型">
              <el-option label="web" value="web" />
              <el-option label="app" value="app" />
              <el-option label="pc" value="pc" />
            </el-select>
          </el-form-item>
          <el-form-item label="项目内容" :label-width="formLabelWidth">
            <el-input v-model="editform.content" autocomplete="off" />
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="edit_dialogFormVisible = false">取 消</el-button>
          <el-button type="primary" @click="handleEditSubmit">确 定</el-button>
          <!--          准备添加事件-->
        </div>
      </el-dialog>

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
          <!--          {{ scope.row.id }}-->
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
          <!--          {{ scope.row.type }}-->
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

          <!--          <el-button-->
          <!--            v-else-->
          <!--            size="mini"-->
          <!--            @click="handleEdit(scope.$index, scope.row)"-->
          <!--          >编辑</el-button>-->

          <el-button
            size="mini"
            type= "success"
            @click="handleEdit(scope.$index, scope.row)"
          >编辑</el-button>

          <el-button
            size="mini"
            type= "danger"
            @click="handleDelete(scope.$index, scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>

    </el-table>
    <!-- 分页 -->
    <el-pagination
      background
      :current-page.sync="listQuery.page"
      :page-sizes="[10,15,20]"
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
  name: 'Projectconfig',

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
      // 绑定搜索数据
      search: {
        type: null,
        content: null
      },
      dialogFormVisible: false, // 添加对话框标识
      edit_dialogFormVisible: false,
      addform: {
        content: null,
        type: null
      },
      editform: {
        id: null,
        content: null,
        type: null
      },
      formLabelWidth: '120px',
      temppage: null,
      templimit: null
    }
  },

  created() {
    this.fetchData()
  },
  methods: {

    fetchData() {
      // 添加username参数
      this.listQuery.username = this.$store.getters.name
      this.listQuery.token = this.$store.getters.token
      this.listLoading = true
      project_config(this.listQuery).then(response => {
        this.list = response.data.items
        console.log(this.list)
        this.total = response.data.total
        this.listQuery.add = null // 避免多次添加
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

    handleEdit(index, row) {
      this.editform.id = row.id
      this.editform.type = row.type
      this.editform.content = row.content
      this.editform.origin_content = row.content
      this.edit_dialogFormVisible = true
    },

    handleEditSubmit() {
      this.$message('编辑后会更改其他关联数据!')
      this.listQuery.edit = this.editform
      this.edit_dialogFormVisible = false
      this.fetchData()
    },

    handleAdd() {
      // this.listQuery.add = this.addform
      this.listQuery.add = JSON.stringify(this.addform)
      console.log(this.listQuery)
      this.addform.content = null
      this.addform.type = null
      this.dialogFormVisible = false
      this.fetchData()
    },

    handleDownload() {
      this.temppage = this.listQuery.page
      this.templimit = this.listQuery.limit

      this.listQuery.page = 1
      this.listQuery.limit = 99999999

      this.downloadData()
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
