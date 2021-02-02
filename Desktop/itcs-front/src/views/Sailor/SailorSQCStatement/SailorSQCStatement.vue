<template>
  <Table
    :viewNewDoc="newDoc"
    labelKeyAdd="newStatementSQC"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="sqc-statements-info"
    type="sailorSQCStatement">
    <SailorSQCStatementAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorSQCStatement.js">

</script>

<style scoped>
  .card .card {
    box-shadow: -8px 12px 18px 0 rgba(25, 42, 70, 0.13) !important;
  }
  .active svg {
    fill: #42627e
  }
</style>
