<template>
  <b-card
    header-tag="header"
    class="pb-2"
  >
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('viewPrice') }} {{ $t(row.item.type_of_form) }} {{ row.item.type_document.value }}
        </div>
        <unicon
          @click="hideDetailed(row)"
          name="multiply"
          fill="#42627e"
          height="20px"
          width="20px"
          class="close"
        />
      </div>
    </template>
    <div v-if="itemsFuture.count">
      <h3>{{ $t('futurePrice') }}</h3>
      <Table
        :items="itemsFuture.results"
        :fields="fields"
        :deleteRow="deletePositionPrice"
        :getDocuments="getFutureValuesInfo"
        type="backOfficeFutureDocumentPrices"
        componentEdit="BackOfficeDocumentPriceEdit"/>
      <Paginate
        :current="itemsFuture.current"
        :next="itemsFuture.next"
        :prev="itemsFuture.previous"
        :count="itemsFuture.count"
        :changePage="getFutureValuesInfo" />
    </div>

    <div v-if="itemsPast.count" class="mt-2">
      <h3>{{ $t('pastPrice') }}</h3>
      <Table
        :items="itemsPast.results"
        :fields="fields"
        :deleteRow="deletePositionPrice"
        :getDocuments="getPastValuesInfo"
        type="backOfficePastDocumentPrices"
        componentEdit="BackOfficeDocumentPriceEdit"/>
      <Paginate
        :current="itemsPast.current"
        :next="itemsPast.next"
        :prev="itemsPast.previous"
        :count="itemsPast.count"
        :changePage="getPastValuesInfo" />
    </div>
    <div v-if="!itemsFuture.count && !itemsPast.count">
      {{ $t('emptyFutureAndPastValues') }}
    </div>
  </b-card>
</template>

<script src="./BackOfficeDocumentsPriceInfo.js"></script>
