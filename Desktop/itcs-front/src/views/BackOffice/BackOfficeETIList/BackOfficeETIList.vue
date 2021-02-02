<template>
  <Table
    :viewNewDoc="newDoc"
    labelKeyAdd="addingListETI"
    :items="items"
    :fields="fields"
    link="list-eti-backoffice-info"
    type="backOfficeETIList">
    <CertificateAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./BackOfficeETIList.js" />
