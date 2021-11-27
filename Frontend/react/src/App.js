import React, { Component} from "react";
import axios from "axios";
import './App.css';

const api = axios.create({
  baseURL: 'http://localhost:5000'
})


class App extends Component{

  state = {
    user: "",
    message: "",
    stockDetails: {
      user: "",
      stockNames: "",
      stockBuyPrices: "",
      cutOffLow: "",
      cutOffHigh: ""
    }
  }

  componentDidMount() {
    let search = window.location.search;
    let params = new URLSearchParams(search);
    let code = params.get('code');
    console.log(code);
    console.log('constructor called');
    api.post('/', {'code': code}).then(res =>{
      if(res.status === 200){
        this.setState({ user: res.data});
        console.log(this.state.user);
      }
    })
 }
  
  constructor(){
    super();
    
  }

  submitStocks = async() => {
    
    var stockNames= document.getElementById("ddlStocks").value;
    var stockBuyPrices = document.getElementById("txtPrice").value;
    var cutOffLow = document.getElementById("txtLow").value;
    var cutOffHigh = document.getElementById("txtHigh").value;

    var username = this.state.user;
    console.log(username);

    console.log("Stock selected: " + stockNames + " and Price is " + stockBuyPrices + "Low : " + cutOffLow + "high : " + cutOffHigh);
    let res = await api.post('/stocks', {username, stockNames, stockBuyPrices, cutOffLow, cutOffHigh});
    if(res.status === 201){
      alert('Submitted');
      document.getElementById("txtPrice").value  = "";
      document.getElementById("txtLow").value  = "";
      document.getElementById("txtHigh").value = "";
      this.setState({message: "Submitted!"})
    }
    else{
      this.setState({message: "Error!"})
    }
  }

  render(){
  return (
    <html>
      <body>

        <head>
          <title>Stock Notification Application</title>

        </head>

        <div class="firstdiv">
          <div class="form-box">


            <div>
              <h1 id="welcome">Welcome Back!</h1>
            </div>
            <div>
              
              <label for="Stocks">Choose a Stock:</label>
              <select name="stocks" id="ddlStocks">
                <option value="CME">CME</option>
                <option value="CBOT">CBOT</option>
                <option value="NY Mercantile">NY Mercantile</option>
                <option value="COMEX">COMEX</option>
                <option value="CCY">CCY</option>
                <option value="NYBOT">NYBOT</option>
                <option value="Chicago Options">Chicago Options</option>
                <option value="CCC">CCC</option>
                <option value="Nasdaq GIDS">Nasdaq GIDS</option>
                <option value="FTSE Index">FTSE Index</option>
                <option value="Osaka">Osaka</option>
              </select>
              <br></br>

            </div>
            <form >
              <p>
              Stock Buy Price : <input  type="text" id="txtPrice" name="price" />
              <br></br>
              </p>
              <p>
              Lower Cutoff : <input  type="text" id="txtLow" name="Lower" />
              <br></br>
              </p>
              Higher Cutoff : <input  type="text" id="txtHigh" name="High" />
              <br></br>

              <p>
               <input class="submit-button" type="button" onClick={this.submitStocks} value="Submit"/>
               </p>
            </form>

          {this.state.message}





          </div>

        </div>

      </body>
    </html>
  )

  }
}

export default App;