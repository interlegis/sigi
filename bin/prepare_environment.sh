#!/bin/bash

cd ${HOME}

# Set .env variables - must be provided in the build process
echo "Setting .env variables..."
echo "DEBUG=${DEBUG}"  >> ${HOME}//sigi/.env
echo "ADMINS=${ADMINS}"  >> ${HOME}//sigi/.env
echo "EMAIL_PORT=${EMAIL_PORT}"  >> ${HOME}//sigi/.env
echo "EMAIL_HOST=${EMAIL_HOST}"  >> ${HOME}//sigi/.env
echo "EMAIL_HOST_USER=${EMAIL_HOST_USER}"  >> ${HOME}//sigi/.env
echo "EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}"  >> ${HOME}//sigi/.env
echo "EMAIL_SUBJECT_PREFIX=${EMAIL_SUBJECT_PREFIX}"  >> ${HOME}//sigi/.env
echo "EMAIL_USE_LOCALTIME=${EMAIL_USE_LOCALTIME}"  >> ${HOME}//sigi/.env
echo "EMAIL_USE_TLS=${EMAIL_USE_TLS}"  >> ${HOME}//sigi/.env
echo "EMAIL_USE_SSL=${EMAIL_USE_SSL}"  >> ${HOME}//sigi/.env
echo "EMAIL_TIMEOUT=${EMAIL_TIMEOUT}"  >> ${HOME}//sigi/.env
echo "DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL}"  >> ${HOME}//sigi/.env
echo "DATABASE_URL=${DATABASE_URL}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_SERVER_URI=${AUTH_LDAP_SERVER_URI}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_BIND_DN=${AUTH_LDAP_BIND_DN}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_BIND_PASSWORD=${AUTH_LDAP_BIND_PASSWORD}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_USER=${AUTH_LDAP_USER}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_USER_SEARCH_STRING=${AUTH_LDAP_USER_SEARCH_STRING}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_GROUP=${AUTH_LDAP_GROUP}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_GROUP_SEARCH_STRING=${AUTH_LDAP_GROUP_SEARCH_STRING}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_GROUP_TYPE_STRING=${AUTH_LDAP_GROUP_TYPE_STRING}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_USER_ATTR_MAP=${AUTH_LDAP_USER_ATTR_MAP}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_PROFILE_ATTR_MAP=${AUTH_LDAP_PROFILE_ATTR_MAP}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_FIND_GROUP_PERMS=${AUTH_LDAP_FIND_GROUP_PERMS}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_MIRROR_GROUPS=${AUTH_LDAP_MIRROR_GROUPS}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_CACHE_GROUPS=${AUTH_LDAP_CACHE_GROUPS}"  >> ${HOME}//sigi/.env
echo "AUTH_LDAP_GROUP_CACHE_TIMEOUT=${AUTH_LDAP_GROUP_CACHE_TIMEOUT}"  >> ${HOME}//sigi/.env
echo "AUTH_PROFILE_MODULE=${AUTH_PROFILE_MODULE}"  >> ${HOME}//sigi/.env
echo "... done"

echo "Data migrations before start..."
python manage.py migrate
echo "...done"
