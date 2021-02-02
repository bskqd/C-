<template>
  <Table
    :items="items"
    :fields="fields"
    link="dealing-backoffice-info"
    type="backOfficeDealing"/>
</template>

<script src="./BackOfficeDealing.js"/>
<style media="screen" scoped>
  .btn-table, thead th:last-child {
    min-width: 0!important;
  }
</style>
