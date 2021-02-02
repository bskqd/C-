<template>
  <div>
    <b-card no-body>
      <ReportSearch
        :education="true"
        report="educationReport"
        ref="search"
        :getReport="getEducationReport"
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
        :getDocuments="getEducationReport"
        link="education-documents-info"
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

<script src="./ReportEducation.js" />
