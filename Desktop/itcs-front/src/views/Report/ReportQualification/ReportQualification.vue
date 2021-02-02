<template>
  <div>
    <b-card no-body>
      <div class="d-flex p-2 text-left">
        <label class="mt-auto mr-2">
          {{ $t('typeDoc') }}:
        </label>
        <b-form-radio-group
          v-model="typeDocument"
          :options="typeDocumentList"
          value-field="id"
          text-field="text"
        />
      </div>
      <ReportSearch
        v-if="typeDocument"
        :qualDocument="typeDocument === 'diplomasQualification'"
        :qualApplication="typeDocument === 'statementQualification'"
        :report="typeDocument"
        ref="search"
        :getReport="getReportQualification"
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
        :getDocuments="getReportQualification"
        link="qualification-documents-info"
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

<script src="./ReportQualification.js" />
