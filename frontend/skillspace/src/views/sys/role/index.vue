<template>
  <div class="role-management">
    <el-card class="page-header">
      <div class="header-actions">
        <h2>角色管理</h2>
        <el-button 
          type="primary" 
          @click="handleAdd"
          v-permission="'system:role:add'"
        >
          <el-icon><Plus /></el-icon>
          新增角色
        </el-button>
      </div>
    </el-card>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="角色名称">
          <el-input v-model="searchForm.name" placeholder="请输入角色名称" clearable />
        </el-form-item>
        <el-form-item label="角色编码">
          <el-input v-model="searchForm.code" placeholder="请输入角色编码" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 角色列表 -->
    <el-card class="table-card">
      <el-table :data="roleList" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="code" label="角色编码" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleEdit(row)"
              v-permission="'system:role:edit'"
            >编辑</el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleAssignMenu(row)"
              v-permission="'system:role:assign'"
            >分配权限</el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
              v-permission="'system:role:delete'"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchRoleList"
        @current-change="fetchRoleList"
      />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入角色编码（如：admin）" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="formData.remark" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配权限对话框 -->
    <el-dialog
      v-model="menuDialogVisible"
      title="分配菜单权限"
      width="600px"
      @open="handleMenuDialogOpen"
    >
      <div class="menu-dialog-content">
        <!-- 角色信息提示 -->
        <el-alert
          :title="`正在为角色 '${currentRoleName}' 分配权限`"
          type="info"
          :closable="false"
          style="margin-bottom: 16px;"
        />

        <!-- 操作工具栏 -->
        <div class="menu-toolbar">
          <div class="toolbar-left">
            <el-button size="small" @click="handleCheckAll">全选</el-button>
            <el-button size="small" @click="handleUncheckAll">取消全选</el-button>
            <el-button size="small" @click="handleExpandAll">展开全部</el-button>
            <el-button size="small" @click="handleCollapseAll">折叠全部</el-button>
          </div>
          <div class="toolbar-right">
            <el-tag type="success">已选: {{ checkedCount }} 项</el-tag>
          </div>
        </div>

        <!-- 权限树 -->
        <div class="menu-tree-container">
          <el-tree
            ref="menuTreeRef"
            :data="menuTreeData"
            show-checkbox
            node-key="id"
            :default-checked-keys="checkedMenuIds"
            :default-expand-all="false"
            :props="{ children: 'children', label: 'name' }"
            :check-strictly="false"
            @check="handleTreeCheck"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <el-icon v-if="data.icon" style="margin-right: 8px;">
                  <component :is="data.icon" />
                </el-icon>
                <span>{{ node.label }}</span>
                <el-tag v-if="data.type" size="small" style="margin-left: 8px;">
                  {{ data.type === 'menu' ? '菜单' : '按钮' }}
                </el-tag>
              </span>
            </template>
          </el-tree>
        </div>
      </div>
      <template #footer>
        <el-button @click="menuDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleMenuSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { roleManagement, menuManagement } from '@/api/auth';

// 数据状态
const loading = ref(false);
const roleList = ref([]);
const searchForm = reactive({
  name: '',
  code: ''
});

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
});

// 对话框状态
const dialogVisible = ref(false);
const dialogTitle = ref('新增角色');
const isEdit = ref(false);
const formRef = ref(null);
const formData = reactive({
  id: null,
  name: '',
  code: '',
  remark: ''
});

const formRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }]
};

// 菜单权限相关
const menuDialogVisible = ref(false);
const menuTreeRef = ref(null);
const menuTreeData = ref([]);
const checkedMenuIds = ref([]);
const currentRoleId = ref(null);
const currentRoleName = ref('');
const checkedCount = ref(0);

// 获取所有节点ID（用于全选）
const getAllNodeIds = (nodes) => {
  const ids = [];
  const traverse = (list) => {
    list.forEach(node => {
      ids.push(node.id);
      if (node.children && node.children.length > 0) {
        traverse(node.children);
      }
    });
  };
  traverse(nodes);
  return ids;
};

// 菜单对话框打开时的处理
const handleMenuDialogOpen = () => {
  // 初始化选中数量
  updateCheckedCount();
};

// 更新选中数量
const updateCheckedCount = () => {
  if (menuTreeRef.value) {
    const checkedKeys = menuTreeRef.value.getCheckedKeys();
    checkedCount.value = checkedKeys.length;
  }
};

// 树节点选中变化时
const handleTreeCheck = () => {
  updateCheckedCount();
};

// 全选
const handleCheckAll = () => {
  const allIds = getAllNodeIds(menuTreeData.value);
  menuTreeRef.value.setCheckedKeys(allIds);
  updateCheckedCount();
};

// 取消全选
const handleUncheckAll = () => {
  menuTreeRef.value.setCheckedKeys([]);
  updateCheckedCount();
};

// 展开全部
const handleExpandAll = () => {
  const expandAllNodes = (nodes) => {
    nodes.forEach(node => {
      menuTreeRef.value.store.nodesMap[node.id].expanded = true;
      if (node.children && node.children.length > 0) {
        expandAllNodes(node.children);
      }
    });
  };
  expandAllNodes(menuTreeData.value);
};

// 折叠全部
const handleCollapseAll = () => {
  const collapseAllNodes = (nodes) => {
    nodes.forEach(node => {
      menuTreeRef.value.store.nodesMap[node.id].expanded = false;
      if (node.children && node.children.length > 0) {
        collapseAllNodes(node.children);
      }
    });
  };
  collapseAllNodes(menuTreeData.value);
};

// 获取角色列表
const fetchRoleList = async () => {
  loading.value = true;
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize
    };
    const response = await roleManagement.getList(params);
    
    // DRF标准分页格式处理
    if (response.results) {
      roleList.value = response.results;
      pagination.total = response.count || 0;
    } else {
      // 兼容非分页格式
      roleList.value = Array.isArray(response) ? response : [];
      pagination.total = roleList.value.length;
    }
  } catch (error) {
    console.error('获取角色列表失败:', error);
    ElMessage.error(error.message || '获取角色列表失败');
    roleList.value = [];
    pagination.total = 0;
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.page = 1;
  fetchRoleList();
};

// 重置
const handleReset = () => {
  searchForm.name = '';
  searchForm.code = '';
  handleSearch();
};

// 新增
const handleAdd = () => {
  isEdit.value = false;
  dialogTitle.value = '新增角色';
  Object.assign(formData, {
    id: null,
    name: '',
    code: '',
    remark: ''
  });
  dialogVisible.value = true;
};

// 编辑
const handleEdit = (row) => {
  isEdit.value = true;
  dialogTitle.value = '编辑角色';
  Object.assign(formData, row);
  dialogVisible.value = true;
};

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await roleManagement.update(formData.id, formData);
          ElMessage.success('更新成功');
        } else {
          await roleManagement.create(formData);
          ElMessage.success('创建成功');
        }
        dialogVisible.value = false;
        fetchRoleList();
      } catch (error) {
        console.error('操作失败:', error);
        ElMessage.error(error.message || '操作失败');
      }
    }
  });
};

// 分配权限
const handleAssignMenu = async (row) => {
  currentRoleId.value = row.id;
  currentRoleName.value = row.name;
  try {
    // 获取菜单树
    const menus = await menuManagement.getTree();
    menuTreeData.value = menus;

    // 获取已分配的菜单
    const roleDetail = await roleManagement.getMenus(row.id);
    if (roleDetail.menus && Array.isArray(roleDetail.menus)) {
      checkedMenuIds.value = roleDetail.menus.map(m => m.id || m);
    } else {
      checkedMenuIds.value = [];
    }

    menuDialogVisible.value = true;
  } catch (error) {
    console.error('获取菜单数据失败:', error);
    ElMessage.error(error.message || '获取菜单数据失败');
  }
};

// 提交菜单权限
const handleMenuSubmit = async () => {
  const checkedKeys = menuTreeRef.value.getCheckedKeys();
  try {
    await roleManagement.assignMenus(currentRoleId.value, checkedKeys);
    ElMessage.success('权限分配成功');
    menuDialogVisible.value = false;
  } catch (error) {
    console.error('权限分配失败:', error);
    ElMessage.error(error.message || '权限分配失败');
  }
};

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该角色吗？', '提示', {
      type: 'warning'
    });
    await roleManagement.delete(row.id);
    ElMessage.success('删除成功');
    fetchRoleList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error(error.message || '删除失败');
    }
  }
};

onMounted(() => {
  fetchRoleList();
});
</script>

<style scoped>
.role-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

/* 菜单权限对话框样式 */
.menu-dialog-content {
  max-height: 600px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.menu-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.menu-tree-container {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
  max-height: 400px;
  background: #fff;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  font-size: 14px;
}

/* 树节点样式优化 */
.menu-tree-container :deep(.el-tree-node__content) {
  height: 36px;
  line-height: 36px;
}

.menu-tree-container :deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}

.menu-tree-container :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: #e6f7ff;
}

/* 复选框样式 */
.menu-tree-container :deep(.el-checkbox__inner) {
  width: 16px;
  height: 16px;
}

/* 展开/折叠图标样式 */
.menu-tree-container :deep(.el-tree-node__expand-icon) {
  font-size: 14px;
  color: #606266;
}

/* 滚动条美化 */
.menu-tree-container::-webkit-scrollbar {
  width: 6px;
}

.menu-tree-container::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.menu-tree-container::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}
</style>
