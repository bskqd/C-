<template>
  <b-card
    header-tag="header"
    class="pb-2"
  >
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('viewAgentStatementFromSailor') }}
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
    <div class="flex-row-sb wrap mt-1">
      <div
        v-for="photo of photoArray"
        :key="photo.url"
        class="col mb-1"
      >
        <a
          :href="photo.url"
          target="_blank"
        >
          <img
            :src="photo.url"
            width="400"
            class="p-1"
            alt="agentStatementsFile"
          />
          <p class="text-center">
            {{ photo.photoName }}
          </p>
        </a>
      </div>
    </div>
  </b-card>
</template>

<script src="./AgentStatementsFiles.js" />
