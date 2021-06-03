<template>
  <div class="app-container">
    <el-form ref="form" :model="form" label-width="120px">
      <span>扫描规则详细配置 :</span>
      <br>
      <br>
      <div class="filter-container">
        <el-row>
          <el-col :span="12" style="display:flex;justify-content:space-between;align-items:center">
            <span>选择配置 :</span>
            <el-select
              v-model="search.configname"
              clearable
              placeholder="选择待查询删除的配置"
            >
              <el-option
                v-for="(item,index) in query.configname"
                :key="index"
                :label="item"
                :value="item"
              />
            </el-select>
            <el-button class="filter-item" type="primary" icon="el-icon-search" @click="searchData">查询</el-button>
            <el-button class="filter-item" type="primary" icon="el-icon-delete" @click="deleteData">删除</el-button>
          </el-col>
          <el-col :span="10" :offset="1" style="align-items:end">
            <el-tooltip class="item" effect="dark" content="提交下面填写的配置" placement="bottom">
              <el-button type="primary" icon="el-icon-upload2" @click="add_onSubmit">新建提交</el-button>
            </el-tooltip>
            <el-tooltip class="item" effect="dark" content="编辑提交下面填写的配置" placement="bottom">
              <el-button type="primary" icon="el-icon-edit" @click="edit_onSubmit">编辑提交</el-button>
            </el-tooltip>
          </el-col>
        </el-row>
      </div>

      <br>
      <br>
      <el-form-item label="配置名称">
        <el-input v-model="form.config_name" />
      </el-form-item>
      <el-form-item label="启动越权">
        <el-switch v-model="form.Judge_out_of_access.status" />
      </el-form-item>
      <el-form-item label="替换cookie">
        <el-input v-model="form.Judge_out_of_access.content.token" />
      </el-form-item>
      <el-form-item label="原始uid">
        <el-input v-model="form.Judge_out_of_access.content.越权uid配置.origin_userid" />
      </el-form-item>
      <el-form-item label="第一个替换uid">
        <el-input v-model="form.Judge_out_of_access.content.越权uid配置.userid_first" />
      </el-form-item>
      <el-form-item label="第二个替换uid">
        <el-input v-model="form.Judge_out_of_access.content.越权uid配置.userid_second" />
      </el-form-item>
      <el-form-item label="启动xss">
        <el-switch v-model="form.Payloadlist_xss.status" />
      </el-form-item>
      <el-form-item label="启动敏感信息">
        <el-switch v-model="form.Check_sensitive_info.status" />
      </el-form-item>
      <el-form-item label="启动数据包分割">
        <el-switch v-model="form.Segment.status" />
      </el-form-item>
      <el-form-item label="启动监控">
        <el-switch v-model="form.Monitor.status" />
      </el-form-item>

    </el-form>

  </div>
</template>

<script>
import { add_rule_config } from '@/api/table'
import FileSaver from 'file-saver'
import XLSX from 'xlsx'

export default {
  name: 'Ruleconfig',

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
      origin_configname: null,
      form: {
        config_name: '',
        Judge_out_of_access: { scan_type_name: 'Judge_out_of_access', scan_type_run_name: 'run_judge_out_of_access', status: false, content: { token: null, 越权uid配置: { origin_userid: null, userid_first: null, userid_second: null }}},
        Payloadlist_xss: { scan_type_name: 'Payloadlist_xss', scan_type_run_name: 'run_payloadlist_xss', status: false, content: null },
        Check_sensitive_info: { scan_type_name: 'Check_sensitive_info', scan_type_run_name: 'run_check_sensitive_info', status: false, content: null },
        Segment: { scan_type_name: 'Segment', scan_type_run_name: 'run_segment', status: false, content: null },
        Monitor: { scan_type_name: 'Monitor', scan_type_run_name: 'run_monitor', status: false, content: null }
      },
      list: null,
      pageList: [], // 当前页数据
      currentPage: 1, // 当前页
      total: 0,
      listLoading: true,
      pagelimit: 2, // 页面展示数据条数
      tmpList: [], // 临时搜索结果数据-->
      pagesize: [10, 15, 20],
      // 绑定搜索数据
      search: {
        configname: ''
      },
      query: {
        configname: null
      },
      listQuery: {
      },
      edit_save_flag_list: [],
      formLabelWidth: '120px',
      temppage: null,
      templimit: null
    }
  },

  created() { // 初始化需要自定义
    this.fetchData()
  },
  methods: {
    searchData() {
      this.listQuery.search = this.search.configname
      this.searchFetchData()
    },
    deleteData() {
      this.listQuery.delete = this.search.configname
      this.fetchData()
      this.search.configname = null
    },

    fetchData() {
      // 添加username参数
      this.listQuery.username = this.$store.getters.name
      this.listQuery.token = this.$store.getters.token
      this.listLoading = true
      add_rule_config(this.listQuery).then(response => {
        console.log(response.data)
        this.query.configname = response.myconfignamelist
      })
    },

    searchFetchData() {
      // 添加username参数
      this.listQuery.username = this.$store.getters.name
      this.listQuery.token = this.$store.getters.token
      this.listLoading = true
      add_rule_config(this.listQuery).then(response => {
        this.form = response.data.items
        this.origin_configname = this.form.config_name
        this.query.configname = response.myconfignamelist
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
    add_onSubmit() {
      this.fetchData()
      this.$message('新建提交成功!')
      this.listQuery.add = this.form
    },
    edit_onSubmit() {
      if (this.origin_configname === this.form.config_name) {
        this.$message('编辑提交成功!')
        // this.listQuery.edit.origin_configname = this.origin_configname
        // this.listQuery.edit.form = this.form
        this.listQuery.edit = { 'origin_configname': this.origin_configname, 'form': this.form }
        console.log(this.listQuery.edit)
        this.fetchData()
      } else {
        this.$message('配置名不可修改!')
      }
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
