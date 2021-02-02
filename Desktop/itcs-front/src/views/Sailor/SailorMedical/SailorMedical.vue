<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="addMedicalCert"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="medical-certificates-info"
    type="sailorMedical">
    <SailorMedicalAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorMedical.js"/>
