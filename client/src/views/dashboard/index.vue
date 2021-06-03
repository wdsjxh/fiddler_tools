<template>
  <div v-if="user_flag" class="dashboard-container">
    <component
      :is="currentRole"
      :data-packet-count="data_packet_count"
      :vulnerable-count="vulnerable_count"
      :project-count="project_count"

      :data-month-count="data_month_count"
      :vulnerable-month-count="vulnerable_month_count"
      :normal-month-count="normal_month_count"
    />
  </div>

  <div v-else class="dashboard-container">
    <component
      :is="currentRole"
      :data-packet-count="data_packet_count"
      :vulnerable-count="vulnerable_count"
      :project-count="project_count"

      :user-count="user_count"

      :data-month-count="data_month_count"
      :vulnerable-month-count="vulnerable_month_count"
      :normal-month-count="normal_month_count"
    />
  </div>

</template>

<script>
import { mapGetters } from 'vuex'
import adminDashboard from './admin'
import userDashboard from './user'
import { dashBoard } from '@/api/user'

export default {
  name: 'Dashboard',
  components: { adminDashboard, userDashboard },
  data() {
    return {
      currentRole: 'adminDashboard',
      listQuery: {},
      data_packet_count: null,
      vulnerable_count: null,
      project_count: null,
      user_count: null,

      user_flag: false,

      data_month_count: [],
      vulnerable_month_count: [],
      normal_month_count: []
    }
  },
  computed: {
    ...mapGetters([
      'roles'
    ])
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      // 添加username参数
      this.listQuery.username = this.$store.getters.name
      this.listLoading = true
      dashBoard(this.listQuery).then(response => {
        console.log('主组件response')
        console.log(response)
        if (!this.roles.includes('admin') && !this.roles.includes('super-admin')) {
          console.log('主组件跳转到父组件user')
          this.currentRole = 'userDashboard'
          this.user_flag = true
        } else {
          console.log('主组件跳转到父组件admin')
          this.user_count = response.data.user_count
          console.log(this.user_count)
        }
        this.data_packet_count = response.data.data_packet_count
        this.vulnerable_count = response.data.vulnerable_count
        this.project_count = response.data.project_count

        this.data_month_count = response.data.data_month_count
        this.vulnerable_month_count = response.data.vulnerable_month_count
        this.normal_month_count = response.data.normal_month_count

        console.log('dashboard page')
        console.log(this.data_month_count)
        console.log(this.vulnerable_month_count)
        console.log(this.normal_month_count)

        this.listLoading = false
      })
    }
  }

}
</script>
