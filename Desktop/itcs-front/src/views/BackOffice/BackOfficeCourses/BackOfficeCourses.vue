<template>
  <Table
    :loader="tableLoader"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    :getDocuments="getCoursesETI"
    type="backOfficeCourse"
    componentInfo="BackOfficeCoursesList">
    <CoursesAdd :getCoursesETI="getCoursesETI" slot="AddBlock"/>
  </Table>
</template>

<script src="./BackOfficeCourses.js" />
