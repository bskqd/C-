<template>
  <div class="vx-navbar-wrapper navbar-default">
    <header
      class="vs-navbar vx-navbar navbar-custom navbar-skelton vs-navbar-null vs-navbar-color-#fff"
      style="background: rgb(255, 255, 255);">
      <div class="vs-con-items">
        <div class="navbar-collapse flex-row-sb">
          <div class="search-block col-6">
            <Search v-if="checkAccess('displaySearch')" />
          </div>
          <div class="col-6 header-right">
            <div class="pr-5 cursor-pointer">
              <router-link
                to="/user-notification"
                replace
              >
                <unicon
                  :class="{'active': active === 'userNotification'}"
                  name="bell"
                  fill="#42627e"
                  height="25px"
                  width="25px"
                  class="topbar-notification"
                />
                <b-badge v-if="userNotification.unchecked_notification" pill>
                  {{ userNotification.unchecked_notification }}
                </b-badge>
              </router-link>
            </div>
            <div class="btn-lang">
              <b-dropdown variant="outline-primary" no-caret >
                <template v-slot:button-content>
                  <img :src="getImgByLang()" :alt="lang" class="h-4 w-15 mr-1">
                  &nbsp;{{ $t(lang) }}
                </template>
                <b-dropdown-item>
                  <img src="@/assets/img/Flag_ua.svg" alt="uk" class="h-4 w-15 mr-1">
                  &nbsp;{{ $t('uk') }}
                </b-dropdown-item>
                <b-dropdown-item>
                  <img src="@/assets/img/Flag_en.svg" alt="en" class="h-4 w-15 mr-1">
                  &nbsp;{{ $t('en') }}
                </b-dropdown-item>
              </b-dropdown>
            </div>
            <div>
              <b-dropdown
                id="dropdown-1"
                class="userName p-0"
                variant="outline-primary"
                right
                no-caret
              >
                <template #button-content>
                  <div>
                    <span class="userName-name">{{ username }}</span>
                    <span class="userName-login">
                      {{ login }}
                      <span v-if="checkAccess('agent')">(ID: {{ userId }})</span>
                    </span>
                  </div>
                </template>
                <b-dropdown-item @click="logout">{{ $t('logout') }}</b-dropdown-item>
              </b-dropdown>
            </div>
          </div>
        </div>
      </div>
    </header>
  </div>
</template>

<script src="./TopBar.js"/>

<style>
  .search-block {
    border-right: 1px solid #dfe3e7;
  }
  .btn[class*="btn-outline-"] {
    font-size: 1.1rem;
  }
  .form-control {
    height: 2.5rem!important;
  }
  .navbar-collapse {
    height: 62px
  }
  .infoBlock {
    position: absolute;
    right: 34rem;
    top: 3rem;
    width: 25rem;
  }
</style>
