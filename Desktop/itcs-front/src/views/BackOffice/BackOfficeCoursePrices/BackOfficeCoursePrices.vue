<template>
  <Table
    labelKeyAdd="addingListETI"
    :viewNewDoc="newDoc"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="price-course-backoffice-info"
    type="backOfficeCoursePrice">
    <BackOfficeCoursePriceAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./BackOfficeCoursePrices.js" />
