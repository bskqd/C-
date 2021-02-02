<template>
  <div>
    <b-card no-body>
      <div class="d-flex p-2 text-left">
        <label class="mt-auto mr-2">
          {{ $t('typeDoc') }}:
        </label>
        <b-form-radio-group
          v-model="typeDocument"
          @input="updateTableCells"
          :options="typeDocumentList"
          value-field="id"
          text-field="text"
        />
      </div>
      <ReportSearch
        v-if="typeDocument"
        :sqcProtocol="typeDocument === 'protocolSQC'"
        :sqcApplication="typeDocument === 'statementSQC'"
        :report="typeDocument"
        ref="search"
        :getReport="getReportSQC"
        :getExcel="setExcelDoc"
      />
    </b-card>
    <b-card>
      <div v-if="typeDocument" class="card-header">
        <div class="card-title">
          <h4 class="text-center">
            {{ $t(typeDocument) }}
          </h4>
        </div>
      </div>

      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :sortBy="sortAcs"
        :sortAcs="sortAcs"
        :sortDesc="sortDesc"
        :getDocuments="getReportSQC"
        :link="typeDocument === 'protocolSQC' ? 'sqc-protocols-info' : 'sqc-statements-info'"
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

<script src="./ReportSQC.js"/>
