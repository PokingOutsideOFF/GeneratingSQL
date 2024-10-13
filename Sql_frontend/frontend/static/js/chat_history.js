function changeSessionStatus(){
    sessionStorage.setItem('loggedOut', 'True')
    sessionStorage.setItem('isLoggedIn', 'False')
    {{request.session.username = 'User'}}
}