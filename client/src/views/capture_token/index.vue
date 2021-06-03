<template>
  <div class="app-container">
    <el-form ref="form" :model="form" label-width="120px">
      <el-form-item label="有效期">
        <el-col :span="11">
          <el-date-picker v-model="form.date" type="date" placeholder="选择日期" style="width: 100%;" />
        </el-col>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">生成</el-button>
        <el-button @click="onCancel">取消</el-button>
      </el-form-item>
      <el-form-item label="抓包token: ">
        <el-col :span="8">
          <el-input
            v-model="result"
            placeholder="申请的token结果"
            :type="passwordType"
          />

        </el-col>
        <span class="show-pwd" @click="showPwd">
          <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
        </span>

      </el-form-item>
      <el-form-item>
        <el-button
          v-clipboard:copy="result"
          v-clipboard:success="onCopy"
          v-clipboard:error="onError"
          type="primary"
          icon="el-icon-document-copy"
        >复制</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { make_capture_token } from '@/api/user'
import VueClipboard from 'vue-clipboard2'
import Vue from 'vue'
Vue.use(VueClipboard)
export default {
  data() {
    return {
      tips: '原始/生成的token',
      result: null,
      form: {
        createflag: '0',
        date: ''
      },
      passwordType: 'password'
    }
  },

  created() {
    this.form.name = this.$store.getters.name
    this.form.token = this.$store.getters.token
    this.fetchData()
  },

  methods: {
    fetchData() {
      make_capture_token(this.form).then(response => {
        if (response.data === 'success') {
          this.result = response.capture_token
          this.form.createflag = '0'
        }
      })
    },
    onCopy: e => {
      alert('你成功复制了 :' + e.text)
    },
    // 复制失败的回调
    onError: e => {
      alert('复制失败')
    },
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    onSubmit() {
      this.fetchData()
      this.$message('提交成功!')
      this.form.createflag = '1'
    },
    onCancel() {
      this.form.date = ''
      this.$message({
        message: 'cancel!',
        type: 'warning'
      })
    }
  }
}
</script>

<style scoped>
.line{
  text-align: center;
}
</style>

