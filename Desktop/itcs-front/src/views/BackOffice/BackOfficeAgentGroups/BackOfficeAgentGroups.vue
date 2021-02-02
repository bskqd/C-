<template>
  <div>
    <Table
      v-if="items.length > 1"
      :loader="tableLoader"
      :items="items"
      :fields="fields"
      :sortBy="sortBy"
      :sortDesc="sortDesc"
      :getDocuments="getAgentGroupList"
      type="backOfficeAgentGroups"
      componentInfo="BackOfficeAgentGroupsList"
      componentEdit="BackOfficeAgentGroupsListEdit"/>

    <Table
      v-else
      :loader="tableLoader"
      :items="items.length ? items[0].agents : []"
      :fields="fieldsAgents"
      :sortBy="sortBy"
      :sortDesc="sortDesc"
      :getDocuments="getAgentGroupList"
      type="backOfficeAgentGroups"
      componentInfo="BackOfficeGroupAgentInfo"
      componentEdit="BackOfficeGroupAgentEdit"/>
  </div>
</template>

<script src="./BackOfficeAgentGroups.js" />
