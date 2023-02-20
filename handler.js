'use strict';

const rp = require('request-promise');
const _ = require('lodash');

const BMS_API_USERNAME = "";
const BMS_API_PASSWORD = "";
const BMS_API_SERVER = process.env.BMS_API_SERVER ? process.env.BMS_API_SERVER : 'https://api.bmsemea.kaseya.com'
const BMS_API_TENANT = "";
const BMS_API_TOP = process.env.BMS_API_TOP ? process.env.BMS_API_TOP : "15";
const POWERBI_API = "";

global.accessToken = '';

function web_call(method, url, payload) {
  return new Promise(function (resolve, reject) {
    const opt = {
      method: method,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'multipart/form-data',
        'Authorization': 'Bearer ' + accessToken
      },
      json: true
    }

    // ugh this is utter shite
    if (url.indexOf("https") != 0) {
      Object.assign(opt, { uri: BMS_API_SERVER + url });
    } else {
      Object.assign(opt, { uri: url });
    }

    if (url.indexOf("/v2/security/authenticate" >= 0)) {
      Object.assign(opt, { form: payload });
    } else {
      Object.assign(opt, { body: payload });
    }

    if (accessToken == '') { 
      delete opt.headers['Content-Type'];
      delete opt.headers['Authorization'];
    }

    console.log('web_call(): calling ' + opt.uri);

    rp(opt).then(function (res) {
      resolve(res);
    }).catch(function (err) {
      console.log('web_call(): FAIL: ', err);
      reject(err);
    })
  });
}

function login() {
  return new Promise(function (resolve, reject) {
    const login_Promise = web_call(
      "POST",
      "/v2/security/authenticate",
      {
        UserName: BMS_API_USERNAME,
        Password: BMS_API_PASSWORD,
        GrantType: "password",
        Tenant: BMS_API_TENANT
      }
    );

    login_Promise.then(function (res) {
      accessToken = res.accessToken;
      console.log('login(): access token received -> ', accessToken);
      resolve(accessToken);
    }).catch(function (err) {
      console.log('login(): FAIL: ', err);
      reject(false);
    })
  });
}

function getTickets() {
  return new Promise(function (resolve, reject) {
    const getTicket_Promise = web_call(
      "GET",
      "/v2/servicedesk/tickets?$orderby=id desc&$top=" + BMS_API_TOP,
      {}
    );

    getTicket_Promise.then(function (res) {
      var ticket_payload = res;
      console.log('getTickets(): received payload, no. of results: ', ticket_payload.TotalRecords);

      var reduced_payload = _.map(ticket_payload.Result, function(object) {
        return _.pick(object, ['accountName', 'dueDate', 'lastActivityUpdate', 'openDate', 'queueName', 'statusName', 'ticketNumber', 'title']);
      });

      var ticketPromises = [];

      var opt = {
        method: "POST",
        uri: POWERBI_API,
        json: reduced_payload
      }

      ticketPromises.push(
        rp(opt)
        .then(function(res) {
            resolve('Success');
          }).catch(function (res) {
            console.log(`fail`);
            console.log(res);
            reject(res);
          })
      );

      Promise.all(ticketPromises).then(function() {
        console.log("getTickets(): all promises should have triggered...");
        resolve();
      });
    }).catch(function (err) {
        console.log('getTickets(): sendToPowerBI(): FAIL: ', err);
        reject(false);
    });
  });
}

module.exports.getBMStickets = async (event) => {
  return new Promise((resolve) => {
    console.log('getBMStickets: triggered');

    login()
    .then((token) => {
      accessToken = token;

      getTickets()
      .then((res) => {
        console.log("ticket work done");

        resolve({
          statusCode: 200,
          body: JSON.stringify({
            message: 'job complete'
          })
        });
      })
    })
  });
};
