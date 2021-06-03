import request from '@/utils/request'

export function vulnerable_details(params) {
  return request({
    url: '/vulnerable_details_mul',
    method: 'get',
    params
  })
}

export function data_packet(params) {
  return request({
    url: '/data_packet_mul',
    method: 'get',
    params
  })
}

export function vulnerable_config(params) {
  return request({
    url: '/vulnerable_config_mul',
    method: 'get',
    params
  })
}

export function project_config(params) {
  return request({
    url: '/project_config_mul',
    method: 'get',
    params
  })
}

export function add_rule_config(data) {
  return request({
    url: '/add_rule_config',
    method: 'post',
    data
  })
}

export function user_config(params) {
  return request({
    url: '/user_config_mul',
    method: 'get',
    params
  })
}
