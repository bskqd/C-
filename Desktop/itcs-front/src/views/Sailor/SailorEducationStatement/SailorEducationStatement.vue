<template>
  <Table
    :viewNewDoc="newDoc"
    labelKeyAdd="addAdvanceTrainingStatement"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    type="educationStatement"
    link="education-statements-info">
    <SailorEducationStatementAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorEducationStatement.js" />

<style scoped>
  .card .card {
    box-shadow: -8px 12px 18px 0 rgba(25, 42, 70, 0.13) !important;
  }
  .active svg {
    fill: #42627e
  }
</style>
