<template>
  <div>
    <b-card no-body>
      <ReportSearch
        :reportCadet="true"
        report="cadetReport"
        ref="search"
        :getReport="getReportCadets"
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
        :getDocuments="getReportCadets"
        link="education-student-info"
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

<script src="./ReportCadet.js" />
