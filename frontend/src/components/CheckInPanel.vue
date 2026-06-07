<template>
    <div class="flex flex-col bg-white rounded w-full py-6 px-4 border-none">
      <h2 class="text-lg font-bold text-gray-900">Hey, {{ employee?.data?.first_name }} 👋</h2>
  
      <template v-if="settings.data?.allow_employee_checkin_from_mobile_app">
        <div class="font-medium text-sm text-gray-500 mt-1.5" v-if="lastLog">
          Last {{ lastLogType }} was at {{ lastLogTime }}
        </div>
        <Button
          class="mt-4 mb-1 drop-shadow-sm py-5 text-base"
          id="open-checkin-modal"
          @click="handleEmployeeCheckin"
        >
          <template #prefix>
            <FeatherIcon
              :name="nextAction.action === 'IN' ? 'arrow-right-circle' : 'arrow-left-circle'"
              class="w-4"
            />
          </template>
          {{ nextAction.label }}
        </Button>
      </template>
  
      <div v-else class="font-medium text-sm text-gray-500 mt-1.5">
        {{ dayjs().format("ddd, D MMMM, YYYY") }}
      </div>
    </div>
  
    <ion-modal
      v-if="settings.data?.allow_employee_checkin_from_mobile_app"
      ref="modal"
      trigger="open-checkin-modal"
      :initial-breakpoint="1"
      :breakpoints="[0, 1]"
    >
      <div class="h-120 w-full flex flex-col items-center justify-center gap-5 p-4 mb-5">
        <div class="flex flex-col gap-1.5 mt-2 items-center justify-center">
          <div class="font-bold text-xl">
            {{ dayjs(checkinTimestamp).format("hh:mm:ss a") }}
          </div>
          <div class="font-medium text-gray-500 text-sm">
            {{ dayjs().format("D MMM, YYYY") }}
          </div>
        </div>
  
        <div class="w-full">
          <label class="block text-sm font-medium text-gray-700">
  Select Project
</label>

<input
  type="text"
  v-model="projectSearch"
  placeholder="Type or click to select project..."
  @focus="isDropdownOpen = true"
  @blur="setTimeout(() => isDropdownOpen = false, 200)" 
  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-sm"
/>

<ul
  v-if="isDropdownOpen && filteredProjects.length"
  class="mt-1 border rounded-md max-h-40 overflow-y-auto bg-white shadow"
>
  <li
    v-for="project in filteredProjects"
    :key="project.name"
    @click="selectProject(project)"
    class="px-3 py-2 cursor-pointer hover:bg-indigo-50 text-sm"
  >
    {{ project.project_name }}
  </li>
</ul>

        </div>
  <!-- Select Cost Center Section -->
        <div class="w-full mt-4">
          <label class="block text-sm font-medium text-gray-700">
            Select Cost Center <span class="text-red-500">*</span>
          </label>

          <input
            type="text"
            v-model="costCenterSearch"
            placeholder="Type or click to select cost center..."
            @focus="isCostCenterDropdownOpen = true"
            @blur="setTimeout(() => isCostCenterDropdownOpen = false, 200)"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          />

          <ul
            v-if="isCostCenterDropdownOpen && filteredCostCenters.length"
            class="mt-1 border rounded-md max-h-40 overflow-y-auto bg-white shadow"
          >
            <li
              v-for="cc in filteredCostCenters"
              :key="cc.name"
              @click="selectCostCenter(cc)"
              class="px-3 py-2 cursor-pointer hover:bg-indigo-50 text-sm"
            >
              {{ cc.cost_center_name }}
            </li>
          </ul>
          
         <div
  v-if="
    departmentDetails &&
    !filteredCostCenters.length &&
    !costCenterSearch
  "
  class="text-xs text-red-400 mt-1"
>
  No cost centers linked to your department were found.
</div>
        </div>
        <template v-if="settings.data?.allow_geolocation_tracking">
          <span v-if="locationStatus" class="font-medium text-gray-500 text-sm">
            {{ locationStatus }}
          </span>
  
          <div v-if="distance !== null && selectedProject && selectedProject !== 'non-project'" class="text-sm text-gray-600">
            You are {{ distance.toFixed(2) }} meters away from the project location.
          </div>
  
          <div class="rounded border-4 translate-z-0 block overflow-hidden w-full h-170">
            <iframe
              width="100%"
              height="170"
              frameborder="0"
              scrolling="no"
              marginheight="0"
              marginwidth="0"
              style="border: 0"
              :src="`https://maps.google.com/maps?q=${latitude},${longitude}&hl=en&z=15&output=embed`"
            >
            </iframe>
          </div>
        </template>
  
        <Button variant="solid" class="w-full py-5 text-sm" @click="submitLog(nextAction.action)">
          Confirm {{ nextAction.label }}
        </Button>
      </div>
    </ion-modal>
  </template>
  
 <script setup>
  import { createResource, createListResource, call, toast, FeatherIcon } from "frappe-ui"
import { computed, inject, ref, onMounted, onBeforeUnmount } from "vue"
import { IonModal, modalController } from "@ionic/vue"
import { watchEffect } from "vue"

const DOCTYPE = "Employee Checkin"

const socket = inject("$socket")
const employee = inject("$employee")
const dayjs = inject("$dayjs")
const checkinTimestamp = ref(null)
const latitude = ref(0)
const longitude = ref(0)
const locationStatus = ref("")
const selectedProject = ref(null)
const distance = ref(null)

// --- Projects State ---
const projects = ref([])
const projectSearch = ref("")
const isDropdownOpen = ref(false)

// --- Cost Centers State ---
const selectedCostCenter = ref(null)
const costCenterSearch = ref("")
const isCostCenterDropdownOpen = ref(false)
const allCostCenters = ref([])
const departmentDetails = ref(null)

// --- Computed Projects Filter ---
const filteredProjects = computed(() => {
  if (!projectSearch.value) return projects.value
  return projects.value.filter(p =>
    p.project_name?.toLowerCase().includes(projectSearch.value.toLowerCase())
  )
})

const selectProject = (project) => {
  selectedProject.value = project
  projectSearch.value = project.project_name
}

// --- Computed Dynamic Cost Center Filtering ---
const allowedCostCenterNames = computed(() => {
  if (!departmentDetails.value || !departmentDetails.value.custom_cost_center) {
    return []
  }
  return departmentDetails.value.custom_cost_center.map(item => item.cost_center)
})

const filteredCostCenters = computed(() => {
  console.log("allowedCostCenterNames", allowedCostCenterNames.value)
  console.log("allCostCenters", allCostCenters.value)

  const filtered = allCostCenters.value.filter(cc =>
    allowedCostCenterNames.value.includes(cc.name)
  )

  console.log("filtered result", filtered)

  return filtered
})

// --- Dynamic Data Fetch Processing ---
async function fetchProjects() {
  let res = await call("frappe.client.get_list", {
    doctype: "Project",
    fields: ["name", "project_name", "custom_location", "is_active"],
    order_by: "project_name asc",
    limit_page_length: 0,
  })
  projects.value = res.filter(project => project.is_active !== "No")
}
const selectCostCenter = (cc) => {
  selectedCostCenter.value = cc
  costCenterSearch.value = cc.cost_center_name || cc.name
  isCostCenterDropdownOpen.value = false
}
watchEffect(() => {
  console.log("Allowed Names:", allowedCostCenterNames.value)

  console.log(
    "Cost Centers:",
    allCostCenters.value.map(cc => ({
      name: cc.name,
      cost_center_name: cc.cost_center_name
    }))
  )

  console.log("Filtered:", filteredCostCenters.value)
})

async function fetchSessionDepartmentAndCostCenters() {
  try {
    console.log("Employee:", employee?.data)

    const deptDoc = await call("frappe.client.get", {
      doctype: "Department",
      name: employee.data.department
    })

    console.log("Department Doc:", deptDoc)

    departmentDetails.value = deptDoc

    const ccList = await call("frappe.client.get_list", {
      doctype: "Cost Center",
      fields: ["name", "cost_center_name"],
      limit_page_length: 0
    })

    console.log("Cost Centers:", ccList)

    allCostCenters.value = ccList

  } catch (err) {
    console.error(err)
  }
}
const settings = createResource({
  url: "hrms.api.get_hr_settings",
  auto: true,
})

const checkins = createListResource({
  doctype: DOCTYPE,
  fields: ["name", "employee", "employee_name", "log_type", "time", "device_id", "custom_project"], 
  filters: {
    employee: employee.data.name,
  },
  orderBy: "time desc",
})
checkins.reload()

const lastLog = computed(() => {
  if (checkins.list.loading || !checkins.data) return {}
  return checkins.data[0]
})

const lastLogType = computed(() => {
  return lastLog?.value?.log_type === "IN" ? "check-in" : "check-out"
})

const nextAction = computed(() => {
  return lastLog?.value?.log_type === "IN"
    ? { action: "OUT", label: "Check Out" }
    : { action: "IN", label: "Check In" }
})

const lastLogTime = computed(() => {
  const timestamp = lastLog?.value?.time
  const formattedTime = dayjs(timestamp).format("hh:mm a")

  if (dayjs(timestamp).isToday()) return formattedTime
  else if (dayjs(timestamp).isYesterday()) return `${formattedTime} yesterday`
  else if (dayjs(timestamp).isSame(dayjs(), "year"))
    return `${formattedTime} on ${dayjs(timestamp).format("D MMM")}`

  return `${formattedTime} on ${dayjs(timestamp).format("D MMM, YYYY")}`
})

function handleLocationSuccess(position) {
  latitude.value = position.coords.latitude
  longitude.value = position.coords.longitude

  locationStatus.value = `
    Latitude: ${Number(latitude.value).toFixed(5)}°,
    Longitude: ${Number(longitude.value).toFixed(5)}°
  `
}

function handleLocationError(error) {
  locationStatus.value = "Unable to retrieve your location"
  if (error) locationStatus.value += `: ERROR(${error.code}): ${error.message}`
}

const fetchLocation = () => {
  if (!navigator.geolocation) {
    locationStatus.value = "Geolocation is not supported by your current browser"
    return false
  } else {
    locationStatus.value = "Locating..."
    navigator.geolocation.getCurrentPosition(handleLocationSuccess, handleLocationError)
    return true
  }
}

const handleEmployeeCheckin = () => {
  checkinTimestamp.value = dayjs().format("YYYY-MM-DD HH:mm:ss")

  if (settings.data?.allow_geolocation_tracking) {
    const locationAccessGranted = fetchLocation()
    if (!locationAccessGranted) {
      toast({
        title: "Error",
        text: "Location access is required to check in.",
        icon: "alert-circle",
        position: "bottom-center",
        iconClasses: "text-red-500",
      })
      return
    }
  }
}

const submitLog = (logType) => {
  const action = logType === "IN" ? "Check-in" : "Check-out"

  // Validation checking to ensure they have chosen a cost center before tracking
  if (!selectedCostCenter.value) {
    toast({
      title: "Validation Missing",
      text: "Please select a verified Cost Center to proceed with this submission.",
      icon: "alert-circle",
      position: "bottom-center",
      iconClasses: "text-red-500",
    })
    return
  }

  // Handle Non-Project State
  if (selectedProject.value && !selectedProject.value.custom_location) {
    checkins.insert.submit(
      {
        employee: employee.data.name,
        log_type: logType,
        time: checkinTimestamp.value,
        latitude: latitude.value,
        longitude: longitude.value,
        custom_project: selectedProject.value.name,
        custom_cost_center: selectedCostCenter.value.name, // Custom property mapped here
      },
      {
        onSuccess() {
          modalController.dismiss()
          checkins.reload()
          toast({
            title: "Success",
            text: `${action} successful `,
            icon: "check-circle",
            position: "bottom-center",
            iconClasses: "text-green-500",
          })
          selectedProject.value = null
          selectedCostCenter.value = null
          costCenterSearch.value = ""
        },
        onError() {
          toast({
            title: "Error",
            text: `${action} failed!`,
            icon: "alert-circle",
            position: "bottom-center",
            iconClasses: "text-red-500",
          })
        },
      }
    )
    return
  }

  if (!selectedProject.value) {
    toast({
      title: "Error",
      text: "Please select a project or Non-Project option to proceed.",
      icon: "alert-circle",
      position: "bottom-center",
      iconClasses: "text-red-500",
    })
    return
  }

  try {
    const geojson = JSON.parse(selectedProject.value.custom_location || '{}')
    let projectLatitude = null
    let projectLongitude = null

    if (geojson.features?.[0]?.geometry?.coordinates) {
      [projectLongitude, projectLatitude] = geojson.features[0].geometry.coordinates
    }

    checkins.insert.submit(
      {
        employee: employee.data.name,
        log_type: logType,
        time: checkinTimestamp.value,
        latitude: latitude.value,
        longitude: longitude.value,
        custom_project: selectedProject.value.name,
        custom_cost_center: selectedCostCenter.value.name, // Custom mapping added here
      },
      {
        onSuccess() {
          modalController.dismiss()
          toast({
            title: "Success",
            text: `${action} successful!`,
            icon: "check-circle",
            position: "bottom-center",
            iconClasses: "text-green-500",
          })
          selectedProject.value = null
          selectedCostCenter.value = null
          costCenterSearch.value = ""
        },
        onError() {
          toast({
            title: "Error",
            text: `${action} failed!`,
            icon: "alert-circle",
            position: "bottom-center",
            iconClasses: "text-red-500",
          })
        },
      }
    )
  } catch (error) {
    toast({
      title: "Error",
      text: "Invalid project location data.",
      icon: "alert-circle",
      position: "bottom-center",
      iconClasses: "text-red-500",
    })
    console.error("Error parsing project location:", error)
  }
}

onMounted(() => {
  socket.emit("doctype_subscribe", DOCTYPE)
  socket.on("list_update", (data) => {
    if (data.doctype == DOCTYPE) {
      checkins.reload()
    }
  })
})

onBeforeUnmount(() => {
  socket.emit("doctype_unsubscribe", DOCTYPE)
  socket.off("list_update")
})

onMounted(() => {
  fetchProjects()
  fetchSessionDepartmentAndCostCenters()
})
</script>