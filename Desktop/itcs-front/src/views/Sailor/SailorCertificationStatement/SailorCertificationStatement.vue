<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="etiStatementAdd"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="certification-statements-info"
    type="certificationStatement">
    <SailorCertificationStatementAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorCertificationStatement.js"/>
