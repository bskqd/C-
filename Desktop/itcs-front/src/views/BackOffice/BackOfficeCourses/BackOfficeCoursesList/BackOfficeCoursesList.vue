<template>
  <b-card header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase text-left">
          {{ $t('departmentForCourseETI', { eti: row.item[labelName] }) }}
          <span v-if="checkAccess('backOffice')">
            (ID: {{ row.item.id }})
          </span>
        </div>
        <unicon
          @click="hideDetailed(row)"
          name="multiply"
          fill="#42627e"
          height="20px"
          width="20px"
          class="close"
        />
      </div>
    </template>
    <Table
      :items="items"
      :fields="fields"
      :sortBy="sortBy"
      :sortDesc="sortDesc"
      link="courses-backoffice-info"
      type="backOfficeCourseLine"/>
  </b-card>
</template>

<script src="./BackOfficeCoursesList.js" />
