<template>
  <div class="role-management">
    <el-card class="page-header">
      <div class="header-actions">
        <h2>角色管理</h2>
        <el-button type="primary" @click="handleAdd">
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
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" size="small" @click="handleAssignMenu(row)">分配权限</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
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
      width="500px"
    >
      <el-tree
        ref="menuTreeRef"
        :data="menuTreeData"
        show-checkbox
        node-key="id"
        :default-checked-keys="checkedMenuIds"
        :props="{ children: 'children', label: 'name' }"
      />
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

// 获取角色列表
const fetchRoleList = async () => {
  loading.value = true;
  try {
    // TODO: 调用后端API
    // const response = await roleAPI.getList(searchForm, pagination);
    // roleList.value = response.data;
    // pagination.total = response.total;
    
    // 模拟数据
    roleList.value = [
      {
        id: 1,
        name: '管理员',
        code: 'admin',
        remark: '系统管理员，拥有所有权限',
        create_time: '2025-01-01 10:00:00'
      },
      {
        id: 2,
        name: '普通用户',
        code: 'common',
        remark: '普通用户角色',
        create_time: '2025-01-01 10:00:00'
      }
    ];
    pagination.total = 2;
  } catch (error) {
    ElMessage.error('获取角色列表失败');
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
        // TODO: 调用后端API
        // if (isEdit.value) {
        //   await roleAPI.update(formData.id, formData);
        // } else {
        //   await roleAPI.create(formData);
        // }
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功');
        dialogVisible.value = false;
        fetchRoleList();
      } catch (error) {
        ElMessage.error('操作失败');
      }
    }
  });
};

// 分配权限
const handleAssignMenu = async (row) => {
  currentRoleId.value = row.id;
  // TODO: 获取菜单树和已分配的菜单
  // const menus = await menuAPI.getTree();
  // const assignedMenus = await roleAPI.getMenus(row.id);
  
  // 模拟数据
  menuTreeData.value = [
    {
      id: 1,
      name: '系统管理',
      children: [
        { id: 11, name: '用户管理' },
        { id: 12, name: '角色管理' },
        { id: 13, name: '菜单管理' }
      ]
    }
  ];
  checkedMenuIds.value = [11, 12];
  menuDialogVisible.value = true;
};

// 提交菜单权限
const handleMenuSubmit = async () => {
  const checkedKeys = menuTreeRef.value.getCheckedKeys();
  try {
    // TODO: 调用后端API
    // await roleAPI.assignMenus(currentRoleId.value, checkedKeys);
    ElMessage.success('权限分配成功');
    menuDialogVisible.value = false;
  } catch (error) {
    ElMessage.error('权限分配失败');
  }
};

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该角色吗？', '提示', {
      type: 'warning'
    });
    // TODO: 调用后端API
    // await roleAPI.delete(row.id);
    ElMessage.success('删除成功');
    fetchRoleList();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
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
</style>
