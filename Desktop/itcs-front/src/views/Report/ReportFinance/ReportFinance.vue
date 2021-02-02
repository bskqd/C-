<template>
  <div>
    <b-card no-body>
      <ReportSearch
        :finance="true"
        report="financialReport"
        ref="search"
        :getReport="getFinancialReport"
      />
    </b-card>
    <b-card>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :getDocuments="getFinancialReport"
        componentInfo="ReportFinanceInfo"
        type="reportFinance"/>

      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="changePage" />
    </b-card>
  </div>
</template>

<script src='./ReportFinance.js'/>
