<template>
  <BaseLayout :pageTitle="__('Timesheet')">
    <template #body>
  <div class="flex flex-col h-screen bg-white overflow-hidden">

    <!-- Header -->
    <div class="p-4 border-b shrink-0 bg-white z-10">
      <h2 class="text-xl font-bold text-gray-900">Create Timesheet</h2>
      <p class="text-sm text-gray-500">
        Welcome, {{ employee?.data?.first_name }} — Draft: {{ currentTimesheetName || "None" }}
      </p>
    </div>

    <!-- Scrollable Content -->
    <div class="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-6 pb-64">

      <!-- Add Time Log -->
      <div class="p-4 space-y-4 bg-gray-50 border rounded-lg shadow-sm">
        <h3 class="font-semibold text-gray-700">Add Time Log</h3>

        <div>
          <label class="block text-xs font-bold text-gray-600 uppercase">
            Activity Type
          </label>
          <select
            v-model="newEntry.activity_type"
            class="mt-1 block w-full rounded-md border-gray-300 text-sm"
          >
            <option value="" disabled>Select Activity</option>
            <option v-for="type in activityTypes" :key="type.name" :value="type.name">
              {{ type.name }}
            </option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-600 uppercase">From Time</label>
            <input
              type="datetime-local"
              v-model="newEntry.from_time"
              class="mt-1 block w-full rounded-md border-gray-300 text-sm"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-600 uppercase">To Time</label>
            <input
              type="datetime-local"
              v-model="newEntry.to_time"
              class="mt-1 block w-full rounded-md border-gray-300 text-sm"
            />
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4">

          <div>
            <label class="block text-xs font-bold text-gray-600 uppercase">Project</label>
            <select
              v-model="newEntry.project"
              class="mt-1 block w-full rounded-md border-gray-300 text-sm"
            >
              <option value="">None</option>
              <option v-for="p in projects" :key="p.name" :value="p.name">
                {{ p.project_name }}
              </option>
            </select>
          </div>
          <div>
  <label class="block text-xs font-bold text-gray-600 uppercase">
    Department
  </label>
  <select
    v-model="newEntry.department"
    class="mt-1 block w-full rounded-md border-gray-300 text-sm"
  >
    <option value="">None</option>
    <option v-for="d in departments" :key="d.name" :value="d.name">
      {{ d.department_name }}
    </option>
  </select>
</div>


          <div>
            <label class="block text-xs font-bold text-gray-600 uppercase">Cost Center</label>
            <select
              v-model="newEntry.custom_cost_center"
              class="mt-1 block w-full rounded-md border-gray-300 text-sm"
            >
              <option value="">None</option>
              <option v-for="cc in costCenters" :key="cc.name" :value="cc.name">
                {{ cc.cost_center_name }}
              </option>
            </select>
          </div>
        </div>

        <Button variant="outline" class="w-full" @click="addLogToTable">
          Add Entry
        </Button>
      </div>

      <!-- Logs -->
      <div>
        <h3 class="font-semibold text-gray-700 mb-2">
          Logs ({{ timeLogs.length }})
        </h3>

        <div
          v-if="timeLogs.length === 0"
          class="text-center py-10 text-gray-400 italic border border-dashed rounded-lg bg-gray-50"
        >
          No logs added yet.
        </div>

        <div v-else class="border rounded-lg overflow-x-auto bg-white shadow-sm">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Activity Type</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">From Time</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">To Time</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Project</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cost Center</th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Action</th>
              </tr>
            </thead>

            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(log, index) in timeLogs" :key="index">
                <td class="px-3 py-3 text-sm font-medium">{{ log.activity_type }}</td>
                <td class="px-3 py-3 text-sm text-gray-500">
                  {{ dayjs(log.from_time).format('HH:mm') }}
                </td>
                <td class="px-3 py-3 text-sm text-gray-500">
                  {{ dayjs(log.to_time).format('HH:mm') }}
                </td>
                <td class="px-3 py-3 text-sm text-gray-500">{{ log.project || '—' }}</td>
                <td class="px-3 py-3 text-sm text-gray-500">{{ log.custom_department || "—" }}</td>
                <td class="px-3 py-3 text-sm text-gray-500">{{ log.custom_cost_center || '—' }}</td>
                <td class="px-3 py-3 text-right">
                  <button
                    class="text-red-500 text-sm font-medium"
                    @click="timeLogs.splice(index, 1)"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Actions -->
      <div class="space-y-3">
        <Button class="w-full py-6 text-lg font-semibold" @click="saveTimesheet(false)">
          Save Draft
        </Button>

      </div>

      <!-- Bottom Spacer -->
      <div class="h-32"></div>

    </div>
  </div>
</template>

  </BaseLayout>
</template>



<style scoped>
/* Ensures momentum scrolling on iOS and hides scrollbar if desired */
.overflow-y-auto {
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE and Edge */
}
.overflow-y-auto::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}
</style>
<script setup>
import { ref, onMounted, inject } from "vue"
import { call, toast, Button } from "frappe-ui"
import BaseLayout from "@/components/BaseLayout.vue"

const employee = inject("$employee")
const dayjs = inject("$dayjs")

/* ------------------ State ------------------ */
const timeLogs = ref([])
const projects = ref([])
const costCenters = ref([])
const activityTypes = ref([])

const latitude = ref(0)
const longitude = ref(0)
const locationStatus = ref("")
const departments = ref([])

const newEntry = ref({
  activity_type: "",
  from_time: "",
  to_time: "",
  project: "",
  department: "",
  custom_cost_center: ""
})


// Track current working Timesheet
const currentTimesheet = ref(null)
const currentTimesheetName = ref("") 

// ------------------ Submit Timesheet ------------------


const isSubmitting = ref(false)
const successMessage = ref("")
const error = ref("")
const submitTimesheetByName = async (timesheetName) => {
  if (!timesheetName) {
    toast({ title: "Error", text: "No Timesheet selected", variant: "error" })
    return
  }

  if (!confirm(`Force submit Timesheet ${timesheetName}?`)) return

  isSubmitting.value = true

  try {
    const res = await call("hrms.api2.submit_timesheet", { name: timesheetName })
    toast({ title: "Success", text: res.message, variant: "success" })

    // Clear local state
    if (currentTimesheet.value?.name === timesheetName) {
      currentTimesheet.value = null
      timeLogs.value = []
      currentTimesheetName.value = ""
    }
  } catch (err) {
    console.error("Force Submit Error:", err)
    toast({ title: "Error", text: err?.message || "Failed to submit", variant: "error" })
  } finally {
    isSubmitting.value = false
  }
}


/* ------------------ Fetch Metadata ------------------ */
const fetchMetadata = async () => {
  const [act, proj, dept, cc] = await Promise.all([
    call("frappe.client.get_list", {
      doctype: "Activity Type",
      fields: ["name"]
    }),
    call("frappe.client.get_list", {
      doctype: "Project",
      fields: ["name", "project_name", "custom_location"],
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


/* ------------------ Distance Utility ------------------ */
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371e3
  const toRad = v => (v * Math.PI) / 180
  const φ1 = toRad(lat1)
  const φ2 = toRad(lat2)
  const Δφ = toRad(lat2 - lat1)
  const Δλ = toRad(lon2 - lon1)
  const a = Math.sin(Δφ/2)**2 + Math.cos(φ1)*Math.cos(φ2)*Math.sin(Δλ/2)**2
  return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)))
}

/* ------------------ Location ------------------ */
const fetchLocation = () => {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      locationStatus.value = "Geolocation not supported"
      resolve(false)
    } else {
      locationStatus.value = "Fetching location..."
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          latitude.value = pos.coords.latitude
          longitude.value = pos.coords.longitude
          locationStatus.value = `Location: ${latitude.value.toFixed(4)}, ${longitude.value.toFixed(4)}`
          resolve(true)
        },
        () => {
          locationStatus.value = "Location access denied"
          resolve(false)
        }
      )
    }
  })
}

/* ------------------ Add Log Entry ------------------ */
const addLogToTable = async () => {
  const locationOk = await fetchLocation()
  if (!locationOk) return

  const e = newEntry.value

  if (
    !e.activity_type ||
    !e.from_time ||
    !e.to_time ||
    !e.project ||
    !e.department
  ) {
    toast({
      title: "Missing Data",
      text: "Activity, time, project and department are required",
      variant: "error"
    })
    return
  }

  timeLogs.value.push({
    activity_type: e.activity_type,
    from_time: e.from_time,
    to_time: e.to_time,
    project: e.project,
    custom_cost_center: e.custom_cost_center,
    custom_department: e.department,
    custom_latitude: latitude.value,
    custom_longitude: longitude.value
  })

  newEntry.value = {
    activity_type: "",
    from_time: "",
    to_time: "",
    project: "",
    department: "",
    custom_cost_center: ""
  }
}



/* ------------------ Load or Create Timesheet ------------------ */
/* Updated Loader to ensure we get the latest info */
const loadTodayDraftTimesheet = async () => {
  try {
    const todayStart = dayjs().startOf("day").format("YYYY-MM-DD HH:mm:ss")
    
    const res = await call("frappe.client.get_list", {
      doctype: "Timesheet",
      filters: {
        employee: employee.data.name,
        docstatus: 0, // 0 = Draft
        creation: [">=", todayStart]
      },
      fields: ["name"],
      order_by: "creation desc",
      limit: 1
    })

    if (res.length) {
      const fullDoc = await call("frappe.client.get", {
        doctype: "Timesheet",
        name: res[0].name
      })
      currentTimesheet.value = fullDoc
      currentTimesheetName.value = fullDoc.name
      // This populates the table with existing logs from the server
      timeLogs.value = fullDoc.time_logs || []
    }
  } catch (err) {
    console.error("Failed to load draft:", err)
  }
}
/* ------------------ Validate Distance ------------------ */
/* const validateDistance = () => {
  for (const log of timeLogs.value) {
    if (!log.project) continue
    const project = projects.value.find(p => p.name === log.project)
    if (!project?.custom_location) continue

    let projLat = 0
    let projLon = 0
    try {
      const geojson = JSON.parse(project.custom_location)
      if (geojson.features?.[0]?.geometry?.coordinates) {
        [projLon, projLat] = geojson.features[0].geometry.coordinates
      } else if (Array.isArray(geojson) && geojson.length === 2) {
        [projLat, projLon] = geojson
      } else if (geojson.lat && geojson.lon) {
        projLat = geojson.lat
        projLon = geojson.lon
      } else {
        throw new Error("Invalid location format")
      }
    } catch {
      toast({ title: "Project Location Error", text: `Invalid location data for ${project.project_name}`, variant: "error" })
      return false
    }

    const distance = calculateDistance(latitude.value, longitude.value, projLat, projLon)
    if (distance > 50) {
      toast({ title: "Too Far From Project", text: `You are ${distance.toFixed(1)}m away from ${project.project_name}. Max 50m allowed.`, variant: "error" })
      return false
    }
  }
  return true
}*/

/* ------------------ Save or Submit Timesheet ------------------ */

const saveTimesheet = async (submit = false) => {
  const locationOk = await fetchLocation()
  if (!locationOk) {
    toast({ title: "Location Required", text: "Location access is required", variant: "error" })
    return
  }

  // if (!validateDistance()) return

  try {
    let finalDocName = ""

    if (currentTimesheet.value) {
  // Update existing draft
  finalDocName = currentTimesheet.value.name

  await call("frappe.client.set_value", {
    doctype: "Timesheet",
    name: finalDocName,
    fieldname: {
      time_logs: timeLogs.value // each log now has lat/lon
    }
  })
} else {
  // Create new draft
  const doc = {
    doctype: "Timesheet",
    employee: employee.data.name,
    time_logs: timeLogs.value // each log already has lat/lon
  }
  const res = await call("frappe.client.insert", { doc })
  finalDocName = res.name
  currentTimesheet.value = res
}


    if (submit) {
  if (!finalDocName) {
    console.warn("Cannot submit: finalDocName is missing")
    toast({
      title: "Submit Failed",
      text: "Timesheet not found. Save draft first.",
      variant: "error"
    })
    return
  }

  try {
    console.log("Submitting Timesheet:", finalDocName)
    await call("frappe.client.submit", { 
      doctype: "Timesheet", 
      name: finalDocName 
    })
    toast({
      title: "Submitted",
      text: "Timesheet submitted successfully",
      variant: "success"
    })
    currentTimesheet.value = null
    timeLogs.value = []
  } catch (e) {
    console.error("Submit Error:", e)
    toast({
      title: "Submit Failed",
      text: e?.message || e?.exc || "Unknown server error",
      variant: "error"
    })
  }
}

  } catch (e) {
    console.error("Error in saveTimesheet:", e)
    toast({ title: "Error", text: e.message || "Failed to save", variant: "error" })
  }
}

/* ------------------ Mounted ------------------ */
onMounted(async () => {
  await fetchMetadata()
  await fetchLocation()
  await loadTodayDraftTimesheet()
})

</script>