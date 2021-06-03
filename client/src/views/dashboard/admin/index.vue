<template>
  <!--  <div  class="dashboard-editor-container">-->
  <div v-if="dataPacketCount" class="dashboard-editor-container">

    <panel-group
      :data-packet-count="dataPacketCount"
      :vulnerable-count="vulnerableCount"
      :project-count="projectCount"
      :user-count="userCount"
      @handleSetLineChartData="handleSetLineChartData"
    />

    <el-row style="background:#fff;padding:16px 16px 0;margin-bottom:32px;">
      <div v-if="dataMonthCount" class="chart-container">
        <mix-chart
          height="100%"
          width="100%"
          :data-month-count="dataMonthCount"
          :vulnerable-month-count="vulnerableMonthCount"
          :normal-month-count="normalMonthCount"
        />
      </div>
    </el-row>

  </div>
</template>

<script>
import PanelGroup from '@/components/Panels/PanelGroup'
import MixChart from '@/components/Charts/MixChart'

const lineChartData = {
  newVisitis: {
    expectedData: [100, 120, 161, 134, 105, 160, 165],
    actualData: [120, 82, 91, 154, 162, 140, 145]
  },
  messages: {
    expectedData: [200, 192, 120, 144, 160, 130, 140],
    actualData: [180, 160, 151, 106, 145, 150, 130]
  },
  purchases: {
    expectedData: [80, 100, 121, 104, 105, 90, 100],
    actualData: [120, 90, 100, 138, 142, 130, 130]
  },
  shoppings: {
    expectedData: [130, 140, 141, 142, 145, 150, 160],
    actualData: [120, 82, 91, 154, 162, 140, 130]
  }
}

export default {
  name: 'DashboardAdmin',
  components: {
    PanelGroup,
    MixChart
  },
  props: {
    dataPacketCount: {
      type: Number,
      default: 666
    },
    vulnerableCount: {
      type: Number,
      default: 666
    },
    projectCount: {
      type: Number,
      default: 666
    },
    userCount: {
      type: Number,
      default: 666
    },

    dataMonthCount: {
      type: Array,
      default() {
        return []
      }
    },
    vulnerableMonthCount: {
      type: Array,
      default() {
        return []
      }
    },
    normalMonthCount: {
      type: Array,
      default() {
        return []
      }
    }
  },
  data() {
    return {
      lineChartData: lineChartData.newVisitis,
      mydataMonthCount: this.dataMonthCount,
      myvulnerableMonthCount: this.vulnerableMonthCount,
      mynormalMonthCount: this.normalMonthCount
    }
  },
  watch: {
    dataMonthCount: {
      handler(newVal) {
        this.mydataMonthCount = newVal
        console.log('刷新页面admin时候')
        console.log(this.mydataMonthCount)
      },
      deep: true // 划重点
    },
    vulnerableMonthCount: {
      handler(newVal) {
        this.myvulnerableMonthCount = newVal
      },
      deep: true // 划重点
    },
    normalMonthCount: {
      handler(newVal) {
        this.mynormalMonthCount = newVal
      },
      deep: true // 划重点
    }
  },
  updated() {
    console.log('父组件update')
    console.log(this.mydataMonthCount)
  },
  methods: {
    handleSetLineChartData(type) {
      this.lineChartData = lineChartData[type]
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-editor-container {
  padding: 32px;
  background-color: rgb(240, 242, 245);
  position: relative;

  .chart-container{
    position: relative;
    width: 100%;
    height: calc(100vh - 84px);
  }

}

</style>
