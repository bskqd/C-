<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="addCertificateETI"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    type="certification"
    link="certification-certificates-info">
    <SailorCertificationAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorCertification.js"/>
