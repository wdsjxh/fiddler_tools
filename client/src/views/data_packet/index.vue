<template>
  <div class="app-container">
    <!--    //搜索查询-->
    <div class="filter-container" style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <span>项目:</span>
        <el-select v-model="search.project" placeholder="请选择">
          <el-option
            v-for="(item,index) in query.project"
            :key="index"
            :label="item"
            :value="item"
          />
        </el-select>
        <span>方法:</span>
        <el-select v-model="search.method" placeholder="请选择">
          <el-option value="GET">GET</el-option>
          <el-option value="POST">POST</el-option>
          <el-option value="none">None</el-option>
        </el-select>
        <span>请求类型：</span>
        <el-select v-model="search.httptype" placeholder="请选择">
          <el-option value="http">http</el-option>
          <el-option value="https">https</el-option>
          <el-option value="none">None</el-option>
        </el-select>
        <span>时间：</span>
        <el-date-picker
          v-model="search.time"
          type="datetimerange"
          format="yyyy-MM-dd HH:mm:ss"
          value-format="yyyy-MM-dd HH:mm:ss"
          :default-time="['12:00:00']"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          align="right"
          @change="dateChange"
        />
      </div>
      <!-- 全局搜索 -->
      <el-input
        v-model="search.value"
        placeholder="请求响应全局搜索"
        style="width:300px;margin-left:18px;margin-top:7px"
        class="filter-item"
        @keyup.enter.native="searchData"
      />
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="searchData">搜索</el-button>
      <el-button class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">
        导出
      </el-button>
    </div>
    <el-table
      v-loading="listLoading"
      class="tableLimit"
      :data="list"
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
      <el-table-column label="请求包">
        <template slot-scope="scope">
          <el-popover trigger="hover" placement="center">
            <pre>{{ scope.row.request }}</pre>
            <div slot="reference" class="name-wrapper">
              <pre>{{ scope.row.request }}</pre>
              <!--              <el-tag><pre>{{ scope.row.request }}</pre></el-tag>-->
            </div>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column label="响应包">
        <template slot-scope="scope">
          <el-popover trigger="hover" placement="center">
            <pre>{{ scope.row.response }}</pre>
            <div slot="reference" class="name-wrapper">
              <pre>{{ scope.row.response }}</pre>
            </div>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column label="方法" width="110" align="center" prop="method" sortable>
        <template slot-scope="scope">
          {{ scope.row.method }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="请求类型" width="110" align="center" prop="type" sortable>
        <template slot-scope="scope">
          {{ scope.row.type }}
        </template>
      </el-table-column>
      <el-table-column align="center" prop="time" label="时间" width="200" sortable>
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.time }}</span>
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
import { data_packet } from '@/api/table'
import XLSX from 'xlsx'

export default {
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
      listLoading: true,
      pageList: [], // 当前页数据
      currentPage: 1, // 当前页
      total: 0,
      pagelimit: 2, // 页面展示数据条数
      tmpList: [], // 临时搜索结果数据-->
      listQuery: {
        page: 1,
        limit: 15
      },
      // 条件列表
      query: {
        project: null
      },
      // 绑定搜索数据
      search: {
        method: null,
        httptype: null,
        value: null,
        key: null,
        time: '',
        startTime: '',
        project: null
      },
      temppage: null,
      templimit: null,
      export_prject: null
    }
  },
  created() {
    this.listQuery.username = this.$store.getters.name
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      data_packet(this.listQuery).then(response => {
        this.list = response.data.items
        // console.log(this.list)
        this.total = response.data.total
        this.query.project = response.data.project
        if (this.listQuery.project !== '0' && this.listQuery.project !== null && this.listQuery.project !== undefined) {
          this.export_prject = this.listQuery.project
        } else {
          this.export_prject = this.query.project[0]
        }
        this.listLoading = false
      })
    },

    downloadData() {
      this.listLoading = true
      data_packet(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.exportXLSX()
        this.listQuery.page = this.temppage
        this.listQuery.limit = this.templimit
        this.fetchData()
        this.listLoading = false
      })
    },

    // 改变页面条数
    handleSizeChange: function(size) {
      this.listQuery.limit = size
      this.fetchData()
    },

    // 改变当前页
    handleCurrentChange: function(currentPage) {
      this.listQuery.page = currentPage
      this.fetchData()
    },
    // 时间确认触发
    dateChange(val) {
      this.search.time = val
    },
    handleDownload() {
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
      return XLSX.writeFile(wb, this.export_prject + '.xlsx')
    },
    // 搜索函数
    searchData() {
      // 搜索标识
      this.listQuery.search = 'search'
      // 项目选择
      if (this.search.project !== null && this.search.project !== '' && this.search.project !== 'none') {
        this.listQuery.project = this.search.project
      } else {
        this.listQuery.project = '0'
      }
      // 类型选择
      if (this.search.httptype !== null && this.search.httptype !== '' && this.search.httptype !== 'none') {
        this.listQuery.httptype = this.search.httptype
        console.log(this.listQuery.httptype)
      } else {
        this.listQuery.httptype = '0'
        console.log(this.listQuery.httptype)
      }
      // 请求方法也选择
      if (this.search.method !== null && this.search.method !== '' && this.search.method !== 'none') {
        this.listQuery.method = this.search.method
        console.log(this.listQuery.method)
      } else {
        this.listQuery.method = '0'
        console.log(this.listQuery.method)
      }
      // 时间
      if (this.search.time !== null && this.search.time !== '') {
        this.listQuery.starttime = this.search.time[0]
        this.listQuery.stoptime = this.search.time[1]
        console.log(this.listQuery.starttime)
        console.log(this.listQuery.stoptime)
      } else {
        this.listQuery.starttime = '0'
        this.listQuery.stoptime = '0'
        console.log(this.listQuery.starttime)
        console.log(this.listQuery.stoptime)
      }
      // 搜索关键字
      if (this.search.value !== null && this.search.value !== '') {
        this.listQuery.value = this.search.value
        console.log(this.listQuery.value)
      } else {
        this.listQuery.value = '0'
        console.log(this.listQuery.value)
      }
      this.fetchData()
    }

  }
}
</script>

<style>
  .el-table tr:hover{
    /*background: #f6faff;*/
    background: #87CEFA;
  }
  .el-table tr {
    background-color: #eaf2ff;
  }
  .el-select .el-input__inner {
    width: 120px;
    display:flex;
    justify-content:space-between;
  }
</style>
