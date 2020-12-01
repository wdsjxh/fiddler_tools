<template>
  <div class="app-container">
    <div class="filter-container" style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <span>项目:</span>
        <el-select
          v-model="search.project"
          clearable
          placeholder="请选择"
        >
          <el-option
            v-for="(item,index) in query.project"
            :key="index"
            :label="item"
            :value="item"
          />
        </el-select>
        <span>方法:</span>
        <el-select
          v-model="search.method"
          clearable
          style="width:8%"
          placeholder="请选择"
        >
          <el-option
            v-for="(item,index) in query.method"
            :key="index"
            :label="item"
            :value="item"
          />
        </el-select>
        <span>类型:</span>
        <el-select
          v-model="search.total_type"
          clearable
          style="width:8%"
          placeholder="请选择"
          @change="handleSelected"
        >
          <el-option
            v-for="(item,index) in query.total_type"
            :key="index"
            :label="item"
            :value="item"
          />
        </el-select>
        <span>漏洞类型:</span>
        <el-select
          v-model="search.details_type"
          clearable
          style="width:13%"
          placeholder="请选择"
        >
          <el-option
            v-for="(item,index) in query.details_type"
            :key="index"
            :label="item"
            :value="item"
          />
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
        style="width:200px;margin-left:18px;margin-top:7px"
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
      :data="list"
      element-loading-text="Loading"
      border
      fit
      highlight-current-row
      stripe
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
      <el-table-column class-name="status-col" label="详情" width="110" align="center" prop="details" sortable>
        <template slot-scope="scope">
          {{ scope.row.details }}
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

import { vulnerable_details } from '@/api/table'
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
      search: {
        value: null,
        key: null,
        time: '',
        startTime: '',
        project: '',
        method: null,
        total_type: '漏洞',
        details_type: null
      },
      tmpList: [], // 临时搜索结果数据-->
      // 条件列表
      query: {
        project: null,
        method: null,
        details_type: null,
        details_type_ori: null,
        total_type: null
      },
      listQuery: {
        page: 1,
        limit: 10
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
      vulnerable_details(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.query.project = response.data.project
        this.query.method = response.data.method
        this.query.details_type = response.data.details_type
        this.query.details_type_ori = response.data.details_type
        this.query.total_type = response.data.total_type
        if (this.listQuery.project !== '0' && this.listQuery.project !== null && this.listQuery.project !== undefined) {
          this.export_prject = this.listQuery.project
        } else {
          this.export_prject = this.query.project[0]
        } // 导出项目名字
        console.log(this.query.project)
        console.log(this.query.method)
        console.log(this.query.total_type)
        this.listLoading = false
      })
    },
    downloadData() {
      this.listLoading = true
      vulnerable_details(this.listQuery).then(response => {
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
      console.log(size)
      this.listQuery.limit = size
      this.fetchData()
    },

    handleSelected: function(value) {
      if (value === '监控') {
        this.query.details_type = ['监控']
      } else if (value === '漏洞') {
        this.query.details_type_ori.splice('监控', 1)
        this.query.details_type = this.query.details_type_ori
      }
    },

    // 改变当前页
    handleCurrentChange: function(currentPage) {
      console.log(currentPage)
      this.listQuery.page = currentPage
      this.fetchData()
    },
    // 时间确认触发
    dateChange(val) {
      this.search.time = val
      console.log(this.search.time)
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
      return XLSX.writeFile(wb, this.export_prject + '.xlsx')
    },
    // 搜索函数
    searchData() {
      this.listQuery.search = 'search'
      // 项目选择
      if (this.search.project !== null && this.search.project !== '' && this.search.project !== 'none') {
        this.listQuery.project = this.search.project
      } else {
        this.listQuery.project = '0'
      }
      // 请求方法选择
      if (this.search.method !== null && this.search.method !== '' && this.search.method !== 'none') {
        this.listQuery.method = this.search.method
        console.log(this.listQuery.method)
      } else {
        this.listQuery.method = '0'
      }
      // 类型选择
      if (this.search.total_type !== null && this.search.total_type !== '' && this.search.total_type !== 'none') {
        this.listQuery.total_type = this.search.total_type
      } else {
        this.listQuery.total_type = '0'
      }
      // 漏洞类型选择
      if (this.search.details_type !== null && this.search.details_type !== '' && this.search.details_type !== 'none') {
        this.listQuery.details_type = this.search.details_type
        console.log(this.listQuery.details_type)
      } else {
        this.listQuery.details_type = '0'
      }
      // 时间
      if (this.search.time !== null && this.search.time !== '') {
        this.listQuery.starttime = this.search.time[0]
        this.listQuery.stoptime = this.search.time[1]
      } else {
        this.listQuery.starttime = '0'
        this.listQuery.stoptime = '0'
      }
      // 搜索关键字
      if (this.search.value !== null && this.search.value !== '') {
        this.listQuery.value = this.search.value
      } else {
        this.listQuery.value = '0'
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
