<template>
  <div class="content-wrapper">
    <div class="router-view">
      <div class="vx-card">
        <b-tabs fill>
          <b-tab
            @click="viewNewNotifications = true"
            active
          >
            <template slot="title">
              <div class="text-uppercase">
                {{ $t('newNotification') }}
                <b-badge
                  v-if="userNotification.unchecked_notification"
                  class="ml-1"
                  pill
                >
                  {{ userNotification.unchecked_notification }}
                </b-badge>
              </div>
            </template>
          </b-tab>
          <b-tab @click="viewNewNotifications = false">
            <template slot="title">
              <div class="text-uppercase">
                {{ $t('clearedNotification') }}
              </div>
            </template>
          </b-tab>
        </b-tabs>

        <div
          v-if="(viewNewNotifications && !newNotifications.length) || (!viewNewNotifications && !clearedNotifications.length)"
          class="no-permission"
        >
          {{ $t('noNotifications') }}
        </div>

        <div v-else>
          <div
            v-for="record of viewNewNotifications ? newNotifications : clearedNotifications"
            :key="record.id"
            class="text-left p-2"
          >
            <b-alert
              :variant="viewNewNotifications ? 'success' : 'light'"
              show
            >
              <div class="d-flex justify-content-between">
                <h4 class="alert-heading m-0">
                  {{ record.title }}
                </h4>
                <div>
                  <a
                    v-if="record.sailor_id"
                    :href="`/seafarer/${record.sailor_id}`"
                    target="_blank"
                    class="mr-1"
                  >
                    <unicon
                      name="user-circle"
                      height="30px"
                      width="30px"
                      fill="#42627e"
                      class="cursor"
                    />
                  </a>
                  <unicon
                    v-if="viewNewNotifications"
                    @click="readNotification(record)"
                    name="check-circle"
                    height="30px"
                    width="30px"
                    fill="#42627e"
                    class="cursor"
                  />
                </div>
              </div>
              <hr class="m-0 mb-1">
              <p>{{ record.text }}</p>
              <router-link
                v-if="record.sectionUrl"
                :to="record.sectionUrl"
                replace
              >
                <span style="color: #5A8DEE;">{{ $t('goToSection') }}</span>
              </router-link>
            </b-alert>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script src="./UserNotification.js" />
<style scoped>
  .active div {
    color: #fff !important
  }
  .alert-success {
    background-color: #bef4da !important;
  }
  .alert-light {
    background-color: #e1e5ea !important;
  }
</style>
<style>
  .tabs-border-none .nav-tabs {
    border: 0 !important;
  }
</style>
