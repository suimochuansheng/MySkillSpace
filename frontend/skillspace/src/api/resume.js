import axios from 'axios'
import Cookies from 'js-cookie' // 引入 cookie 工具

export function diagnoseResume(formData) {
  // 获取 Django 设置的 CSRF Token (通常存在 cookie 里，key 叫 csrftoken)
  const csrfToken = Cookies.get('csrftoken')

  return axios({
    url: '/api/resume/diagnose/', // 确保路径正确
    method: 'post',
    data: formData,
    
    // 🔥 关键点 1：允许携带 Cookie (sessionid)
    withCredentials: true, 
    
    headers: {
      // 🔥 关键点 2：手动带上 Django 需要的 CSRF 头
      'X-CSRFToken': csrfToken, 
      
      // 不设置 Content-Type，让浏览器自动生成
    }
  }).then(res => {
    return res.data
  })
}