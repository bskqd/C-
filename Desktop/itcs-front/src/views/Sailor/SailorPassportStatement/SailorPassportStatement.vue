<template>
  <Table
    :viewNewDoc="newDoc"
    labelKeyAdd="sailorPassportStatementAdded"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="passports-statements-info"
    type="sailorPassportStatement">
    <SailorPassportStatementAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorPassportStatement.js" />

<style scoped>
  .card .card {
    box-shadow: -8px 12px 18px 0 rgba(25, 42, 70, 0.13) !important;
  }
  .active svg {
    fill: #42627e
  }
</style>
