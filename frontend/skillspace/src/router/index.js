// src/router/index.js
{
  path: '/resume-diagnose',
  name: 'ResumeDiagnose',
  component: () => import('@/views/resume/ResumeDiagnose.vue'), // 懒加载
  meta: { title: 'AI 简历诊断', icon: 'el-icon-document' }
}