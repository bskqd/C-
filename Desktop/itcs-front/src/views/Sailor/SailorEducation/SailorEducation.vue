<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="addNewEducationDoc"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="education-documents-info"
    type="education">
    <SailorEducationAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorEducation.js"/>

<style scoped>
  .card .card {
    box-shadow: -8px 12px 18px 0 rgba(25, 42, 70, 0.13) !important;
  }
  .active svg {
    fill: #42627e
  }
</style>
