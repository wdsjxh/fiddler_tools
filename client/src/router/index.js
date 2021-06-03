import Vue from 'vue'
import Router from 'vue-router'
/* Layout */
import Layout from '@/layout'

Vue.use(Router)

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','user']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/register',
    component: () => import('@/views/register/index'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },

  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: '首页', icon: 'dashboard' }
    }]
  },

  {
    path: '/data_packet',
    component: Layout,
    redirect: '/data_packet/data_packet',
    name: 'Example',
    meta: { title: '漏洞详情', icon: 'el-icon-s-help' },
    children: [
      {
        path: 'vulnerable_details',
        name: 'Vulnerable_details',
        component: () => import('@/views/vulnerable_details/index'),
        meta: { title: '漏洞详情', icon: 'table' }
      },
      {
        path: 'data_packet',
        name: 'Data_packet',
        component: () => import('@/views/data_packet/index'),
        meta: { title: '数据包', icon: 'table' }
      },
      {
        path: 'vulnerable_config',
        name: 'Vulnerable_config',
        component: () => import('@/views/vulnerable_config/index'),
        meta: { title: '抓包过滤配置', icon: 'setting' }
      }
    ]
  },
  {
    path: '/project_config',
    component: Layout,
    redirect: '/project_config/project_config',
    name: 'project_config',
    meta: { title: '项目配置', icon: 'setting-fill' },
    children: [
      {
        path: 'my_project_config',
        name: 'my_project_config',
        component: () => import('@/views/project_config/index'),
        meta: { title: '项目配置', icon: 'setting' }
      },
      {
        path: 'scan_config',
        name: 'scan_config',
        component: () => import('@/views/scan_config/index'),
        meta: { title: '扫描任务启动配置', icon: 'setting' }
      },
      {
        path: 'rule_config',
        name: 'rule_config',
        component: () => import('@/views/rule_config/index'),
        meta: { title: '扫描规则配置', icon: 'setting' }
      }
    ]
  },

  {
    path: '/person_space',
    component: Layout,
    redirect: '/example/person_space',
    name: 'person_space',
    meta: { title: '个人中心', icon: 'form' },
    children: [
      {
        path: 'index',
        name: 'Form',
        component: () => import('@/views/capture_token/index'),
        meta: { title: '抓包配置申请', icon: 'form' }
      }
    ]
  }

]

export const asyncRoutes = [
  {
    path: '/system_config',
    component: Layout,
    redirect: '/system_config/user_config',
    name: 'system_config',
    alwaysShow: true,
    meta: { title: '系统配置', icon: 'setting-fill', roles: ['super-admin', 'admin'] },
    children: [
      {
        path: 'user_config',
        name: 'user_config',
        component: () => import('@/views/user_config/index'),
        meta: { title: '用户管理', icon: 'user', roles: ['super-admin', 'admin'] }
      }
    ]
  },
  {
    path: '/help',
    component: Layout,
    redirect: '/help',
    children: [{
      path: 'help',
      name: 'Help',
      component: () => import('@/views/help/index'),
      meta: { title: '帮助文档', icon: 'link' }
    }]
  },

  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }

]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
