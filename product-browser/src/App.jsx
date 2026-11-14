import ProductPage from './pages/productpage'
import{Routes,Route,Link} from 'react-router'
import BrowsePage from './pages/BrowsePage.jsx'
import ProductDetailPage from './pages/ProductDetailPage.jsx'
function App() {

  return (
    <>
    <nav>
      <Link to ="/">All Products</Link> <Link to ="/browse">Browse</Link>
    </nav>
      <Routes>
        <Route path ="/" element ={<ProductPage/>}/>
        <Route path ="/browse" element ={<BrowsePage/>}/>
        <Route path ="/product/:id" element ={<ProductDetailPage/>}/>
        <Route path ="*" element = {<h1>404 Not Found</h1>}/> 
      </Routes>

     </>
  )
}

export default App
