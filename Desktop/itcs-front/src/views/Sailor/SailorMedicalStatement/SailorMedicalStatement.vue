<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="addMedicalCert"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="medical-statements-info"
    type="medicalStatement">
    <SailorMedicalStatementAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorMedicalStatement.js" />
