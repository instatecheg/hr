<template>
  <BaseLayout :pageTitle="__('Timesheet')">
    <template #body>
      <div class="app-wrapper">
        
        <header class="main-header">
          <div class="header-content">
            <h2 class="title">Create Timesheet</h2>
            <p class="subtitle">Draft: {{ currentTimesheetName || "New Document" }}</p>
          </div>
          <div class="header-emp">
            <span class="emp-label">Employee</span>
            <span class="emp-name">{{ employee?.data?.first_name }}</span>
          </div>
        </header>

        <main class="content-scroll">
          
          <div class="card-form">
            <h3 class="section-title">Add Time Log</h3>

            <div class="input-field">
              <label>Activity Type <span class="star">*</span></label>
              <select v-model="newEntry.activity_type" class="native-input">
                <option value="" disabled>Select Activity</option>
                <option v-for="type in activityTypes" :key="type.name" :value="type.name">{{ type.name }}</option>
              </select>
            </div>

            <div class="input-field">
              <label>From Time <span class="star">*</span></label>
              <input type="datetime-local" v-model="newEntry.from_time" class="native-input" />
            </div>

            <div class="input-field">
              <label>To Time <span class="star">*</span></label>
              <input type="datetime-local" v-model="newEntry.to_time" class="native-input" />
            </div>

            <div class="input-field">
              <label>Project <span class="star">*</span></label>
              <select v-model="newEntry.project" class="native-input">
                <option value="">None</option>
                <option v-for="p in projects" :key="p.name" :value="p.name">{{ p.project_name }}</option>
              </select>
            </div>

            <div class="input-row">
              <div class="input-field">
                <label>Department</label>
                <select v-model="newEntry.department" class="native-input">
                  <option value="">None</option>
                  <option v-for="d in departments" :key="d.name" :value="d.name">{{ d.department_name }}</option>
                </select>
              </div>
              <div class="input-field">
                <label>Cost Center <span class="star">*</span></label>
                <select v-model="newEntry.custom_cost_center" class="native-input">
                  <option value="">None</option>
                  <option v-for="cc in costCenters" :key="cc.name" :value="cc.name">{{ cc.cost_center_name }}</option>
                </select>
              </div>
            </div>

            <button class="btn-primary" @click="addLogToTable">Add Entry</button>
          </div>

          <div v-if="timeLogs.length > 0" class="summary-container">
            <div class="summary-divider">
               <h2>Summary ({{ timeLogs.length }})</h2>
            </div>

            <div v-for="(log, index) in timeLogs" :key="index" class="log-entry-card">
              <div class="log-header">
                <span class="badge">{{ log.activity_type }}</span>
                <button @click="timeLogs.splice(index, 1)" class="btn-remove">✕</button>
              </div>
              
              <div class="log-body">
                <p><strong>Project:</strong> {{ log.project_display }}</p>
                <p><strong>Time:</strong> {{ dayjs(log.from_time).format('HH:mm') }} - {{ dayjs(log.to_time).format('HH:mm') }}</p>
                <div class="log-meta">
                  <span><strong>Dept:</strong> {{ log.dept_display }}</span>
                  <span><strong>CC:</strong> {{ log.cc_display }}</span>
                </div>
                <div class="gps-info">
                  📍 GPS: {{ log.custom_latitude?.toFixed(5) }}, {{ log.custom_longitude?.toFixed(5) }}
                </div>
              </div>
            </div>

            <button class="btn-submit" @click="saveTimesheet(false)">
              Save Timesheet Draft
            </button>
          </div>

          <div v-else class="empty-state">
             No logs added yet.
          </div>

          <div class="spacer"></div>
        </main>
      </div>
    </template>
  </BaseLayout>
</template>

<script setup>
import { ref, onMounted, inject } from "vue"
import { call, toast } from "frappe-ui"
import BaseLayout from "@/components/BaseLayout.vue"

const employee = inject("$employee")
const dayjs = inject("$dayjs")

const timeLogs = ref([])
const projects = ref([])
const costCenters = ref([])
const activityTypes = ref([])
const departments = ref([])
const latitude = ref(0)
const longitude = ref(0)
const currentTimesheet = ref(null)
const currentTimesheetName = ref("")

const newEntry = ref({
  activity_type: "",
  from_time: "",
  to_time: "",
  project: "",
  custom_department: "",
  custom_cost_center: ""
})

/* ================= FETCH META ================= */

const fetchMetadata = async () => {
  const [act, proj, dept, cc] = await Promise.all([
    call("frappe.client.get_list", {
      doctype: "Activity Type",
      fields: ["name"]
    }),
    call("frappe.client.get_list", {
      doctype: "Project",
      fields: ["name", "project_name"],
      filters: { is_active: "Yes" }
    }),
    call("frappe.client.get_list", {
      doctype: "Department",
      fields: ["name", "department_name"]
    }),
    call("frappe.client.get_list", {
      doctype: "Cost Center",
      fields: ["name", "cost_center_name"]
    })
  ])

  activityTypes.value = act
  projects.value = proj
  departments.value = dept
  costCenters.value = cc
}

/* ================= GPS ================= */

const fetchLocation = () => {
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        latitude.value = pos.coords.latitude
        longitude.value = pos.coords.longitude
        resolve(true)
      },
      () => resolve(false),
      { enableHighAccuracy: true }
    )
  })
}

/* ================= ADD LOG ================= */

const addLogToTable = async () => {
  const locationOk = await fetchLocation()
  if (!locationOk) {
    toast({ title: "Error", text: "Location required!", variant: "error" })
    return
  }

  const e = newEntry.value

  if (!e.activity_type || !e.from_time || !e.to_time || !e.project || !e.custom_cost_center) {
    toast({
      title: "Missing Data",
      text: "Please fill all mandatory fields",
      variant: "error"
    })
    return
  }

  const selectedProj = projects.value.find(p => p.name === e.project)
  const selectedDept = departments.value.find(d => d.name === e.custom_department)
  const selectedCC = costCenters.value.find(c => c.name === e.custom_cost_center)

  timeLogs.value.unshift({
    activity_type: e.activity_type,
    from_time: e.from_time,
    to_time: e.to_time,
    project: e.project,
    project_display: selectedProj ? selectedProj.project_name : e.project,

    custom_cost_center: e.custom_cost_center,
    cc_display: selectedCC ? selectedCC.cost_center_name : e.custom_cost_center,

    custom_department: e.custom_department,
    dept_display: selectedDept ? selectedDept.department_name : (e.custom_department || "—"),

    custom_latitude: latitude.value,
    custom_longitude: longitude.value
  })

  newEntry.value = {
    activity_type: "",
    from_time: "",
    to_time: "",
    project: "",
    custom_department: "",
    custom_cost_center: ""
  }
}

/* ================= SAVE ================= */

const saveTimesheet = async () => {
  try {
    let finalDocName = ""

    const logsToSave = timeLogs.value.map(log => ({
      activity_type: log.activity_type,
      from_time: log.from_time,
      to_time: log.to_time,
      project: log.project,
      custom_cost_center: log.custom_cost_center,
      custom_department: log.custom_department,
      custom_latitude: log.custom_latitude,
      custom_longitude: log.custom_longitude
    }))

    if (currentTimesheet.value) {
      finalDocName = currentTimesheet.value.name

      await call("frappe.client.set_value", {
        doctype: "Timesheet",
        name: finalDocName,
        fieldname: {
          time_logs: logsToSave
        }
      })

    } else {
      const doc = {
        doctype: "Timesheet",
        employee: employee.data.name,
        time_logs: logsToSave
      }

      const res = await call("frappe.client.insert", { doc })

      finalDocName = res.name
      currentTimesheet.value = res
      currentTimesheetName.value = res.name
    }

    toast({
      title: "Success",
      text: "Saved successfully",
      variant: "success"
    })

  } catch (e) {
    toast({
      title: "Error",
      text: e.message || "Failed to save",
      variant: "error"
    })
  }
}

/* ================= LOAD DRAFT ================= */

const loadTodayDraftTimesheet = async () => {
  try {
    const todayStart = dayjs().startOf("day").format("YYYY-MM-DD HH:mm:ss")

    const res = await call("frappe.client.get_list", {
      doctype: "Timesheet",
      filters: {
        employee: employee.data.name,
        docstatus: 0,
        creation: [">=", todayStart]
      },
      fields: ["name"],
      limit: 1
    })

    if (!res.length) return

    const fullDoc = await call("frappe.client.get", {
      doctype: "Timesheet",
      name: res[0].name
    })

    currentTimesheet.value = fullDoc
    currentTimesheetName.value = fullDoc.name

    timeLogs.value = (fullDoc.time_logs || []).map(log => {
      const p = projects.value.find(proj => proj.name === log.project)
      const c = costCenters.value.find(cc => cc.name === log.custom_cost_center)
      const d = departments.value.find(dept => dept.name === log.custom_department)

      return {
        ...log,
        project_display: p ? p.project_name : log.project,
        cc_display: c ? c.cost_center_name : log.custom_cost_center,
        dept_display: d ? d.department_name : (log.custom_department || "—")
      }
    })

  } catch (err) {
    console.error(err)
  }
}

onMounted(async () => {
  await fetchMetadata()
  await fetchLocation()
  await loadTodayDraftTimesheet()
})
</script>

<style scoped>
.app-wrapper { background-color: #f1f5f9; height: 100vh; display: flex; flex-direction: column; font-family: sans-serif; }
.main-header { background: #ffffff; padding: 16px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 1.25rem; font-weight: 800; color: #1e293b; margin: 0; }
.subtitle { font-size: 0.75rem; color: #10b981; font-weight: 700; text-transform: uppercase; }
.emp-label { display: block; font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
.emp-name { font-size: 0.875rem; font-weight: 700; color: #334155; }
.content-scroll { flex: 1; overflow-y: auto; padding: 16px; scrollbar-width: none; }
.content-scroll::-webkit-scrollbar { display: none; }

.card-form { background: #ffffff; border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 24px; }
.section-title { font-size: 0.85rem; font-weight: 900; color: #334155; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 15px; }

.input-field { margin-bottom: 16px; }
.input-field label { display: block; font-size: 0.7rem; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 6px; }
.star { color: #ef4444; }
.native-input { width: 100%; height: 44px; border: 1px solid #cbd5e1; border-radius: 10px; padding: 0 12px; font-size: 0.9rem; box-sizing: border-box; transition: border-color 0.2s; }
.native-input:focus { border-color: #10b981; outline: none; }

.input-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.btn-primary { 
  width: 100%; height: 48px; background-color: #0f172a; color: #ffffff; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; transition: all 0.3s ease; 
}
.btn-primary:hover { background-color: #334155; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2); }

.summary-container { margin-top: 24px; }
.summary-divider { text-align: center; border-bottom: 2px solid #cbd5e1; margin-bottom: 20px; padding-bottom: 10px; }
.summary-divider h2 { font-size: 1.1rem; font-weight: 900; color: #1e293b; margin: 0; text-transform: uppercase; }

.log-entry-card { background: #ffffff; border-left: 6px solid #10b981; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.log-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.badge { background: #ecfdf5; color: #047857; padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
.btn-remove { background: transparent; border: none; color: #f87171; font-weight: bold; cursor: pointer; }

.log-body p { font-size: 0.85rem; margin: 4px 0; color: #475569; }
.log-body strong { color: #1e293b; }
.log-meta { display: flex; gap: 15px; font-size: 0.85rem; margin: 8px 0; }
.gps-info { margin-top: 10px; padding-top: 8px; border-top: 1px dashed #e2e8f0; color: #0891b2; font-weight: 600; font-size: 0.8rem; }

.btn-submit { 
  width: 100%; height: 56px; background-color: #10b981; color: #ffffff; border: none; border-radius: 16px; font-size: 1.1rem; font-weight: 800; margin-top: 20px; box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.2); cursor: pointer; transition: all 0.3s ease; 
}
.btn-submit:hover { background-color: #059669; transform: scale(1.02); box-shadow: 0 12px 20px -3px rgba(16, 185, 129, 0.3); }

.empty-state { text-align: center; padding: 40px 0; color: #94a3b8; font-style: italic; }
.spacer { height: 120px; }
</style>
