<template>
  <div>
    <b-card no-body>
      <ReportSearch
        :etiCertificate="true"
        report="certificatesReport"
        ref="search"
        :getReport="getReportETI"
        :getExcel="setExcelDoc"
      />
    </b-card>
    <b-card>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :sortBy="sortAcs"
        :sortAcs="sortAcs"
        :sortDesc="sortDesc"
        :getDocuments="getReportETI"
        link="certification-certificates-info"
        type="report"/>

      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="changePage" />
    </b-card>
  </div>
</template>

<script src="./ReportETI.js" />
