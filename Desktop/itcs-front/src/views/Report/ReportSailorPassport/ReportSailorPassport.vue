<template>
  <div>
    <b-card no-body>
      <ReportSearch
        :sailorPassport="true"
        report="sailorPassportReport"
        ref="search"
        :getReport="getSailorPassportReport"
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
        :getDocuments="getSailorPassportReport"
        link="passports-sailors-info"
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

<script src="./ReportSailorPassport.js" />
