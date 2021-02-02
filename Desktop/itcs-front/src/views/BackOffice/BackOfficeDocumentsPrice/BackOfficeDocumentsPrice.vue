<template>
  <Table
    :viewNewDoc="viewAddBlock"
    labelKeyAdd="addPrice"
    :loader="tableLoader"
    :items="items"
    :fields="fields"
    :getDocuments="getPrice"
    type="backOfficeDocumentPrices"
    componentInfo="BackOfficeDocumentPriceInfo">
    <BackOfficeDocumentsPriceAdd :getDocuments="getPrice" slot="AddBlock"/>
  </Table>
</template>

<script src="./BackOfficeDocumentsPrice.js"></script>
