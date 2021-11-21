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
  }

  
  constructor(){
    super();
    let search = window.location.search;
    let params = new URLSearchParams(search);
    let code = params.get('code');
    console.log(code);
    api.post('/', {'code': code}).then(res =>{
      if(res.status === 200){
        this.setState({ user: res.data});
      }
    })
  }

  submitStocks = async() => {
  let res = await api.post('/stocks', { /* TODO */ });
    if(res.status === 201){
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
          <title>Change Values</title>

        </head>

        <div class="firstdiv">
          <div class="form-box">


            <div>
              <h1 id="welcome">Welcome Back!</h1>
            </div>
            <div>
              <label for="Stocks">Choose a Stock:</label>
              <select name="stocks" id="stock name">
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
              Price : <input  type="text" id="Price" name="price" />
              <br></br>
              Lower Cutoff : <input  type="text" id="Lower" name="Lower" />
              <br></br>
              Higher Cutoff : <input  type="text" id="High" name="High" />
              <br></br>
               <input type="button" onClick={this.submitStocks} value="Submit"/>
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

