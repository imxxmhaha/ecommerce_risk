<template>
  <div class="page">
    <div class="page-title">
      <h2>用户权限</h2>
      <el-button type="primary" @click="openCreate">新增用户</el-button>
    </div>

    <el-tabs v-model="activeTab" class="panel">
      <el-tab-pane label="后台用户" name="users">
        <el-table :data="users">
          <el-table-column prop="username" label="账号" />
          <el-table-column prop="real_name" label="姓名" />
          <el-table-column label="角色">
            <template #default="{ row }">
              <el-tag v-for="role in row.roles" :key="role" class="tag">{{ role }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120" />
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button size="small" @click="toggleStatus(row)">{{ row.status === 'enabled' ? '停用' : '启用' }}</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="userQuery.page"
            v-model:page-size="userQuery.page_size"
            :page-sizes="[10, 20, 50, 100]"
            :total="userTotal"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadUsers"
            @current-change="loadUsers"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="角色" name="roles">
        <el-table :data="roles">
          <el-table-column prop="role_code" label="角色编码" />
          <el-table-column prop="role_name" label="角色名称" />
          <el-table-column prop="description" label="说明" />
          <el-table-column label="权限数" width="100">
            <template #default="{ row }">{{ row.permissions?.length || 0 }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="权限点" name="permissions">
        <el-table :data="permissions">
          <el-table-column prop="permission_code" label="权限编码" />
          <el-table-column prop="permission_name" label="权限名称" />
          <el-table-column prop="permission_type" label="类型" width="120" />
          <el-table-column prop="description" label="说明" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" title="新增后台用户" width="460px">
      <el-form :model="form" label-width="88px">
        <el-form-item label="账号"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.real_name" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_codes" multiple>
            <el-option v-for="role in roles" :key="role.role_code" :label="role.role_name" :value="role.role_code" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createSystemUser, listSystemPermissions, listSystemRoles, listSystemUsers, setSystemUserStatus } from '../api/system'

const activeTab = ref('users')
const dialogVisible = ref(false)
const users = ref<any[]>([])
const userTotal = ref(0)
const userQuery = ref({ page: 1, page_size: 20 })
const roles = ref<any[]>([])
const permissions = ref<any[]>([])
const form = reactive({ username: '', real_name: '', password: '', role_codes: [] as string[] })

function openCreate() {
  Object.assign(form, { username: '', real_name: '', password: '', role_codes: [] })
  dialogVisible.value = true
}

async function loadUsers() {
  const userData = await listSystemUsers(userQuery.value)
  users.value = userData.items || []
  userTotal.value = userData.total || 0
}

async function load() {
  const [_, roleData, permissionData] = await Promise.all([
    loadUsers(),
    listSystemRoles(),
    listSystemPermissions()
  ])
  roles.value = roleData || []
  permissions.value = permissionData || []
}

async function createUser() {
  await createSystemUser({ ...form, status: 'enabled' })
  ElMessage.success('用户已创建')
  dialogVisible.value = false
  load()
}

async function toggleStatus(row: any) {
  await setSystemUserStatus({ user_id: row.id, status: row.status === 'enabled' ? 'disabled' : 'enabled' })
  ElMessage.success('状态已更新')
  load()
}

onMounted(load)
</script>

<style scoped>
.tag {
  margin-right: 6px;
}
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
