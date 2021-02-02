<template>
  <b-card header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('groupInfo') }} "{{ row.item.name_ukr }}"
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
    <Table
      :items="row.item.agents"
      :fields="fieldsAgents"
      :sortBy="sortBy"
      :sortDesc="sortDesc"
      :getDocuments="getDocuments"
      type="backOfficeAgentGroups"
      componentInfo="BackOfficeGroupAgentInfo"
      componentEdit="BackOfficeGroupAgentEdit"/>
  </b-card>
</template>

<script src="./BackOfficeAgentGroupsList.js" />
