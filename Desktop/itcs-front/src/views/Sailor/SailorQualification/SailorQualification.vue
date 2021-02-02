<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="addQualificationDoc"
    :items="items"
    :fields="fields"
    link="qualification-documents-info"
    type="qualification">
    <SailorQualificationAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorQualification.js"/>
