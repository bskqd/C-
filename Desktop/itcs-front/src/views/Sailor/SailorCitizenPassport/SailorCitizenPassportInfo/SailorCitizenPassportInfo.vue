<template>
  <div class="text-left">
    <div class="w-100">
      <b>{{ $t('citizenship') }}:</b>
      {{ Object.keys(data).length ? data.country[labelValue] : '' }}
    </div>

    <div class="w-50 mt-1">
      <b>{{ $t('serialAndNum') }}:</b>
      {{ Object.keys(data).length ? data.serial : '' }}
    </div>

    <div class="w-50 mt-1">
      <b>{{ $t('taxNumber') }}:</b>
      {{ Object.keys(data).length ? data.inn : '' }}
    </div>

    <div class="w-50 mt-1">
      <b>{{ $t('dateIssue') }}:</b>
      {{ Object.keys(data).length ? getDateFormat(data.date) : '' }}
    </div>

    <div class="w-50 mt-1">
      <b>{{ $t('passportIssued') }}:</b>
      {{ Object.keys(data).length ? data.issued_by : '' }}
    </div>

    <div class="w-100 mt-1">
      <b>{{ $t('registrationDoc') }}:</b>
      {{ Object.keys(data).length && data.city_registration ?
        `${data.city_registration.index}, ${data.city_registration.city.country[labelValue]},
         ${data.city_registration.city.region[labelValue]}, ${data.city_registration.city.city[labelValue]},
         ${data.city_registration.street}, ${data.city_registration.house}, ${data.city_registration.flat}` : '' }}
    </div>

    <div class="w-100 mt-1">
      <b>{{ $t('residentPlace') }}:</b>
      {{ Object.keys(data).length && data.resident ?
        `${data.resident.index}, ${data.resident.city.country[labelValue]},
         ${data.resident.city.region[labelValue]}, ${data.resident.city.city[labelValue]}, ${data.resident.street},
         ${data.resident.house}, ${data.resident.flat}` : ''}}
    </div>
  </div>
</template>

<script src="./SailorCitizenPassportInfo.js"/>
