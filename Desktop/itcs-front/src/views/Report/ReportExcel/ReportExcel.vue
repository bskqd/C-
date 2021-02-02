<template>
  <div>
    <b-card>
      <Table
        :loader="tableLoader"
        :items="items"
        :fields="fields"
        :sortBy="sortBy"
        :sortDesc="sortDesc"
        :getDocuments="getExcelDocuments"
        :saveExcel="saveExcelDocument"
        type="reportExcel"/>
    </b-card>
  </div>
</template>

<script src="./ReportExcel.js" />
